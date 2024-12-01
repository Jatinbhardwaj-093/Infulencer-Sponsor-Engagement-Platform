from flask import Flask,render_template,url_for,redirect,flash,request,session,Response
from models import admin, influencer, sponsor, campaign, influencer_ad_request, sponsor_request,Img
from app import app,db
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import config

bcrypt = Bcrypt(app)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/admin_logout")
def admin_logout():
    session.pop('admin_name',None)
    return redirect(url_for("index"))
@app.route("/influencer_logout")
def influencer_logout():
    session.pop('influencer_name',None)
    return redirect(url_for("index"))
@app.route("/sponsor_logout")
def sponsor_logout():
    session.pop('sponsor_name',None)
    return redirect(url_for("index"))


@app.route("/admin_login",methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form['name']
        passaword = request.form['passaword']
        founduser=admin.query.filter_by(username=name).first()
        if not founduser:
            flash('User Does Not Exist')
            return redirect(url_for("admin_login"))
        else:
            confirm_passaword = bcrypt.check_password_hash(founduser.passaword, passaword) # returns True
            
            if confirm_passaword:
                return redirect(url_for("admin_home"))
            else:
                flash('Wrong Password')
                return redirect(url_for("admin_login"))
    else:
        return render_template('admin_login.html')

@app.route("/admin_home",methods=['GET','POST'])
def admin_home():
    if request.method == 'POST':    
        if 'flag' in request.form:
            influencer_id = request.form['influencer_id']
            flag = request.form['flag']
            user = influencer.query.filter_by(influencer_id=influencer_id).first()
            user.flag = flag
            db.session.commit()
            return redirect(url_for("admin_home"))
        if 'delete' in request.form:
            influencer_id = request.form['influencer_id']
            user = influencer.query.filter_by(influencer_id=influencer_id).first()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("admin_home"))
        if 'flag_sponsor'  in request.form:
            sponsor_id = request.form['sponsor_id']
            flag = request.form['flag_sponsor']
            user = sponsor.query.filter_by(sponsor_id=sponsor_id).first()
            user.flag = flag
            db.session.commit()
            return redirect(url_for("admin_home"))
        if 'delete_sponsor'  in request.form:
            sponsor_id = request.form['sponsor_id']
            user = sponsor.query.filter_by(sponsor_id=sponsor_id).first()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("admin_home"))
    
    influencers = influencer.query.all()
    sponsors = sponsor.query.all()
    return render_template('admin_home.html',influencers=influencers,sponsors=sponsors)

@app.route("/influencer_stats")
def influencer_stats():

    # Query the database to get the count of each genre
    niche_results = db.session.query(influencer.genre, db.func.count(influencer.influencer_id)).group_by(influencer.genre).all()
    niche_count_list = [(genre, count) for genre, count in niche_results]
    labels = [row[0] for row in niche_count_list ]
    data = [row[1] for row in niche_count_list ]
    
    # Query the database to get the count of each platform
    platform_result = db.session.query(influencer.platform, db.func.count(influencer.influencer_id)).group_by(influencer.platform).all()
    platform_count_list = [(platform, count) for platform, count in platform_result]
    labels2 = [row[0] for row in platform_count_list ]
    data2 = [row[1] for row in platform_count_list ]
    
    #Query the influencer by flagged condition
    flag_result = db.session.query(influencer.flag, db.func.count(influencer.influencer_id)).group_by(influencer.flag).all()

    results = db.session.query(db.func.count().filter(influencer.flag == 'yes').label('Flagged'),db.func.count().filter(influencer.flag == 'no').label('Ethical')).all()
    flag_count_list = [('yes', results[0][0]), ('no', results[0][1])]
    labels3 = [row[0] for row in flag_count_list ]
    data3 = [row[1] for row in flag_count_list ]
    
    #information of influencer
    influencer_count = db.session.query(db.func.count(influencer.influencer_id)).scalar()
    subquery = db.session.query(influencer.genre).distinct().subquery()
    unique_genre_count = db.session.query(db.func.count()).select_from(subquery).scalar()
    subquery2 = db.session.query(influencer.platform).distinct().subquery()
    unique_platform_count = db.session.query(db.func.count()).select_from(subquery2).scalar()
    flag_count = db.session.query(db.func.count(influencer.influencer_id)).filter(influencer.flag == 'yes').scalar()
    unflag_count = db.session.query(db.func.count(influencer.influencer_id)).filter(influencer.flag == 'no').scalar()
    influencer_request_count = db.session.query(db.func.count(influencer_ad_request.influencer_request_id)).scalar()
    

    info_influencer =[influencer_count,unique_genre_count,unique_platform_count,flag_count,unflag_count,influencer_request_count]
    
    return render_template('influencer_stats.html',labels=labels,data=data,labels2=labels2,data2=data2,labels3=labels3,data3=data3,influencer=info_influencer)

@app.route("/sponsor_stats")
def sponsor_stats():
    
    # Query for count of campaign per industry
    results = db.session.query(sponsor.industry, db.func.count(sponsor.sponsor_id)).group_by(sponsor.industry).all()
    industry_count_list = [(industry, count) for industry, count in results]
    labels = [row[0] for row in industry_count_list ]
    data = [row[1] for row in industry_count_list ]
    
    # Query the database to get the count of campaign per user
    results = db.session.query(sponsor.sponsor_id, sponsor.username, db.func.count(campaign.campaign_id)).outerjoin(campaign, sponsor.sponsor_id == campaign.sponsor_id) .group_by(sponsor.sponsor_id, sponsor.username).all()
    sponsor_campaign_list = [(sponsor_id, sponsor_name, count) for sponsor_id, sponsor_name, count in results]
    labels2 = [row[1] for row in sponsor_campaign_list]
    data2 = [row[2] for row in sponsor_campaign_list]
    
    #Query by sponsor flagged condition
    results = db.session.query(db.func.count().filter(sponsor.flag == 'yes').label('Flagged'),db.func.count().filter(sponsor.flag == 'no').label('Ethical')).all()
    flag_count_list = [('yes', results[0][0]), ('no', results[0][1])]
    labels3 = [row[0] for row in flag_count_list ]
    data3 = [row[1] for row in flag_count_list ]
    
    #information of sponsor
    sponsor_count = db.session.query(db.func.count(sponsor.sponsor_id)).scalar()
    subquery = db.session.query(sponsor.industry).distinct().subquery()
    unique_industry_count = db.session.query(db.func.count()).select_from(subquery).scalar()
    flag_count = db.session.query(db.func.count(sponsor.sponsor_id)).filter(sponsor.flag == 'yes').scalar()
    unflag_count = db.session.query(db.func.count(sponsor.sponsor_id)).filter(sponsor.flag == 'no').scalar()
    sponsor_request_count = db.session.query(db.func.count(sponsor_request.sponsor_request_id)).scalar()
    
    info_sponsor =[sponsor_count,unique_industry_count,flag_count,unflag_count,sponsor_request_count]
    
    return render_template('sponsor_stats.html',labels=labels,data=data,labels2=labels2,data2=data2,labels3=labels3,data3=data3,sponsor = info_sponsor)

@app.route("/campaign_stats",methods=['GET','POST'])
def campaign_stats():
    if request.method == 'POST':
        if 'flag' in request.form:
            campaign_id = request.form['campaign_id']
            flag = request.form['flag']
            user = campaign.query.filter_by(campaign_id=campaign_id).first()
            user.flag = flag
            db.session.commit()
            return redirect(url_for("campaign_stats"))
        
    campaigns= db.session.query(sponsor, campaign).join(campaign).all()
    
    # visibility count of campaigns by [public,private]
    results = db.session.query(campaign.visiblity, db.func.count(campaign.campaign_id)).group_by(campaign.visiblity).all()
    campaign_count_list = [(campaign_type, count) for campaign_type, count in results]
    labels = [row[0] for row in campaign_count_list ]
    data = [row[1] for row in campaign_count_list ]

    # niche of campaign when campaign is private
    results = db.session.query(campaign.finding_niche, db.func.count(campaign.campaign_id)).filter(campaign.visiblity == 'Private').group_by(campaign.finding_niche).all()
    niche_campaign_list = [(niche, count) for niche, count in results]
    
    labels2 = [row[0] for row in niche_campaign_list ]
    data2 = [row[1] for row in niche_campaign_list ]
    
    # Query the database to get the count of campaign per user
    results = db.session.query(sponsor.sponsor_id, sponsor.username, db.func.count(campaign.campaign_id)).outerjoin(campaign, sponsor.sponsor_id == campaign.sponsor_id) .group_by(sponsor.sponsor_id, sponsor.username).all()
    sponsor_campaign_list = [(sponsor_id, sponsor_name, count) for sponsor_id, sponsor_name, count in results]
    
    
    labels3 = [row[1] for row in sponsor_campaign_list]
    data3 = [row[2] for row in sponsor_campaign_list]
    
    
    return render_template('campaign_stats.html',campaigns=campaigns,labels=labels,data=data,labels2=labels2,data2=data2,labels3=labels3,data3=data3)

@app.route("/view_campaign")
def view_campaign():
    campaign_id = int(request.args.get('campaign_id'))
    campaigns= db.session.query(sponsor, campaign).join(campaign).filter(campaign.campaign_id == campaign_id).all()
    return render_template('view_campaign.html',campaign=campaigns)

@app.route("/influencer_login",methods=['GET','POST'])
def influencer_login():
    if request.method == 'POST':
        name = request.form['name']
        passaword = request.form['passaword']
        founduser=influencer.query.filter_by(username=name).first()
        
        if not founduser:
            flash('User Does Not Exist')
            return redirect(url_for("influencer_login"))
        else:
            if founduser.flag=='yes':
                flash('User Is Flagged')
                return redirect(url_for("influencer_login"))
            else:
                confirm_passaword = bcrypt.check_password_hash(founduser.passaword, passaword) # returns True
                if confirm_passaword:
                    session['influencer_name']=name
                    return redirect(url_for("influencer_home"))
                else:
                    flash('Wrong Password')
                    return redirect(url_for("influencer_login"))
    else:
        return render_template('influencer_login.html')

@app.route("/influencer_register",methods=['GET','POST'])
def influencer_register():
    if request.method == 'POST':
        name = request.form['name']
        passaword = request.form['passaword']
        pw_hash = bcrypt.generate_password_hash(passaword)
        genre = request.form['genre']
        email = request.form['email']
        platform = request.form['platform']
        popularity = request.form['popularity']
        
        founduser=influencer.query.filter_by(username=name).first()
        if founduser:
            flash('User Already Exist')
            redirect(url_for("influencer_register"))
        else:
            
            new=influencer(username=name,passaword=pw_hash,genre=genre,email=email,platform=platform,popularity=popularity)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for("influencer_login"))
    else:
        return render_template('influencer_register.html')

@app.route("/influencer_profile_edit",methods=['GET','POST'])
def influencer_profile_edit():
    if request.method == 'POST':
        if "influencer_name" in session:
            influencer_name = session['influencer_name']
            founduser=influencer.query.filter_by(username=influencer_name).first()
            founduser.username = request.form['name']
            founduser.passaword = bcrypt.generate_password_hash(request.form['passaword'])
            founduser.genre = request.form['genre']
            founduser.email = request.form['email']
            founduser.platform = request.form['platform']
            founduser.popularity = request.form['popularity']
            session['influencer_name']=founduser.username   
            db.session.commit()
            
            # upload
            img_influencer = Img.query.filter_by(influencer_id=founduser.influencer_id).first()
            if img_influencer is not None:
                pic = request.files['pic']
                if pic:
                    filename = secure_filename(pic.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    pic.save(filepath)
                    mimetype = pic.mimetype
                    Image = img_influencer
                    Image.name = filename
                    Image.filepath = filepath
                    Image.mimetype = mimetype
                    db.session.commit()
                    
            else:
                pic = request.files['pic']
                if pic:
                    filename = secure_filename(pic.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    pic.save(filepath)
                    mimetype = pic.mimetype
                    Image = Img(name=filename, filepath=filepath, mimetype=mimetype,influencer_id=founduser.influencer_id)
                    db.session.add(Image)
                    db.session.commit()
            
        
            return redirect(url_for("influencer_home"))
    else:
        influencer_name = session['influencer_name']
        founduser=influencer.query.filter_by(username=influencer_name).first()
        #Image

        Image = db.session.query(Img).filter(Img.influencer_id==founduser.influencer_id).first()
        if Image is not None:
            response = Image
        
        else:
            response = 'none'
        return render_template('influencer_profile_edit.html',founduser=founduser,profile=response)


@app.route("/influencer_home",methods=['GET','POST'])
def influencer_home():
    if request.method == 'POST':
        influencer_call = request.form['influencer_call']
        sponsor_request_id = request.form['sponsor_request_id']
        paritcular_sponsor_ad_request = sponsor_request.query.filter_by(sponsor_request_id=sponsor_request_id).first()
        if influencer_call == 'Approve':
            paritcular_sponsor_ad_request.sponsor_status = 'Approved'
        elif influencer_call == 'reject':
            paritcular_sponsor_ad_request.sponsor_status = 'Rejected'
            
        paritcular_sponsor_ad_request.influencer_call = influencer_call
        db.session.commit()
        return redirect(url_for("influencer_home"))
    
    if "influencer_name" in session:
        name = session['influencer_name']
        
        # influencer ad request
        founduser=influencer.query.filter_by(username=name).first()
        influencerRequest = db.session.query(influencer_ad_request,campaign,sponsor).join(campaign,campaign.campaign_id==influencer_ad_request.campaign_id).join(sponsor,sponsor.sponsor_id==influencer_ad_request.sponsor_id)
        influencer_request=influencerRequest.filter(influencer_ad_request.influencer_id==founduser.influencer_id).all()
        
        # sponsor request
        sponsorRequest = db.session.query(sponsor_request,campaign,sponsor).join(campaign,campaign.campaign_id==sponsor_request.campaign_id).join(sponsor,sponsor.sponsor_id==sponsor_request.sponsor_id)
        sponsor_requests=sponsorRequest.filter(sponsor_request.influencer_id==founduser.influencer_id).all()
        
        
        
        #Image

        Image = db.session.query(Img).filter(Img.influencer_id==founduser.influencer_id).first()
        if Image is not None:
            response = Image
        
        else:
            response = 'none'
        

        return render_template('influencer_home.html',founduser=founduser,influencer_requests=influencer_request,sponsor_requests=sponsor_requests,profile=response)
    
@app.route("/find_campaign",methods=['GET','POST'])
def find_campaign():
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        session['campaign_id'] = campaign_id
        return redirect(url_for("influencer_request"))
    else:
        influencer_name = session['influencer_name']
        current_influencer = influencer.query.filter_by(username=influencer_name).first()
        influencer_id = current_influencer.influencer_id
        
        requested_campaign = influencer_ad_request.query.filter_by(influencer_id=influencer_id).all() 
        campaigns = db.session.query(sponsor, campaign).join(campaign).filter(campaign.flag == 'no').all()
        return render_template('find_campaign.html',Campaigns=campaigns,requested_campaign=requested_campaign)

@app.route("/influencer_request",methods=['GET','POST'])
def influencer_request():
    influencer_name = session['influencer_name']
    campaign_idstr =request.args.get('campaign_id')
    campaign_id = int(campaign_idstr)
    if request.method == 'POST':
        influencer_id = influencer.query.filter_by(username=influencer_name).first().influencer_id
        message = request.form['message']
        offer = request.form['offer']
        found_campaign = campaign.query.filter_by(campaign_id=campaign_id).first()
        sponsor_id = found_campaign.sponsor_id
        influencer_request = influencer_ad_request(campaign_id=campaign_id, influencer_id=influencer_id,sponsor_id=sponsor_id,message=message,amount=offer)
        db.session.add(influencer_request)
        db.session.commit()
        return redirect(url_for("find_campaign"))

    return render_template('influencer_request.html')

@app.route("/influencer_active_campaign",methods=['GET','POST'])
def influencer_active_campaign():
    if request.method == 'POST':
        project_submission = request.form['project_submission']
        whoes_request =request.form['whoes_request']
        completed_campaign_idstr = request.form['completed_campaign_id']
        completed_campaign_id = int(completed_campaign_idstr)
        if whoes_request == 'influencer':
            found_campaign = influencer_ad_request.query.filter_by(influencer_request_id=completed_campaign_id).first()
            found_campaign.status_complete_influencer = project_submission 
            db.session.commit()
            
        elif whoes_request == 'sponsor':
            found_campaign = sponsor_request.query.filter_by(sponsor_request_id=completed_campaign_id).first()
            found_campaign.status_complete_influencer = project_submission 
            db.session.commit()
    
    name = session['influencer_name']
        
    founduser=influencer.query.filter_by(username=name).first()
    influencerRequest = db.session.query(influencer_ad_request,campaign,sponsor).join(campaign,campaign.campaign_id==influencer_ad_request.campaign_id).join(sponsor,sponsor.sponsor_id==influencer_ad_request.sponsor_id)
    influencer_requests=influencerRequest.filter(influencer_ad_request.influencer_id==founduser.influencer_id,influencer_ad_request.sponsor_call=='Approved').all()
        
    sponsorRequest = db.session.query(sponsor_request,campaign,sponsor).join(campaign,campaign.campaign_id==sponsor_request.campaign_id).join(sponsor,sponsor.sponsor_id==sponsor_request.sponsor_id)
    sponsor_requests=sponsorRequest.filter(sponsor_request.influencer_id==founduser.influencer_id,sponsor_request.influencer_call=='Approve').all()
    
    
    return render_template('influencer_active_campaign.html' ,influencer_requests=influencer_requests,sponsor_requests=sponsor_requests)






@app.route("/sponsor_login",methods=['POST','GET'])
def sponsor_login():
    if request.method == 'POST':
        name = request.form['name']
        passaword = request.form['passaword']
        founduser=sponsor.query.filter_by(username=name).first()
        if not founduser:
            flash('User Does Not Exist')
            return redirect(url_for("sponsor_login"))
        else:
            if sponsor.flag == 'yes':
                flash('User is Flagged')
                return redirect(url_for("sponsor_login"))
            else:
                confirm_passaword = bcrypt.check_password_hash(founduser.passaword, passaword) # returns True
                if confirm_passaword:
                    session['sponsor_name']=name
                    return redirect(url_for("sponsor_home"))
                
                else:
                    flash('Wrong Password')
                    return redirect(url_for("sponsor_login"))
    else:
        return render_template('sponsor_login.html')
    
@app.route("/sponsor_register",methods=['POST','GET'])
def sponsor_register():
    if request.method == 'POST':
        name = request.form['name']
        passaword = request.form['passaword']
        pw_hash = bcrypt.generate_password_hash(passaword)
        industry = request.form['industry']
        email = request.form['email']
        
        founduser=sponsor.query.filter_by(username=name).first()
        if founduser:
            flash('User Already Exist')
            return redirect(url_for("sponsor_register"))
        else:
            
            new=sponsor(username=name,passaword=pw_hash,industry=industry,email=email)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for("sponsor_login"))
    else:
        return render_template('sponsor_register.html')

@app.route("/sponsor_home",methods=['GET','POST'])
def sponsor_home():
    if request.method == 'POST':
        sponsor_call = request.form['sponsor_call']
        influencer_request_id = request.form['influencer_request_id']
        paritcular_influencer_ad_request = influencer_ad_request.query.filter_by(influencer_request_id=influencer_request_id).first()
        if sponsor_call == 'Approved':
            paritcular_influencer_ad_request.influencer_status = 'Approved'
        elif sponsor_call == 'Rejected':
            paritcular_influencer_ad_request.influencer_status = 'Rejected'
            
        paritcular_influencer_ad_request.sponsor_call = sponsor_call
        db.session.commit()
        return redirect(url_for("sponsor_home"))
    
    if "sponsor_name" in session:
        name = session['sponsor_name']
        
        # influencer ad request
        founduser=sponsor.query.filter_by(username=name).first()
        influencerRequest = db.session.query(influencer_ad_request,campaign,influencer).join(campaign,campaign.campaign_id==influencer_ad_request.campaign_id).join(influencer,influencer.influencer_id==influencer_ad_request.influencer_id)
        influencer_request=influencerRequest.filter(influencer_ad_request.sponsor_id==founduser.sponsor_id).all()

        # sponsor request
        sponsorRequest = db.session.query(sponsor_request,campaign,influencer).join(campaign,campaign.campaign_id==sponsor_request.campaign_id).join(influencer,influencer.influencer_id==sponsor_request.influencer_id)
        sponsor_requests=sponsorRequest.filter(sponsor_request.sponsor_id==founduser.sponsor_id).all()

        return render_template('sponsor_home.html',founduser=founduser,influencer_requests=influencer_request,sponsor_requests=sponsor_requests)
    return render_template('sponsor_home.html')

@app.route("/sponsor_campaign",methods=['GET','POST'])
def sponsor_campaign():
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        return redirect(url_for("sponsor_campaign_edit",campaign_id=campaign_id))
    else:
        sponsor_name=session['sponsor_name']
        found_sponsor=sponsor.query.filter_by(username=sponsor_name).first()
        sponsor_id_find=found_sponsor.sponsor_id
        campaigns=campaign.query.filter_by(sponsor_id=sponsor_id_find).all()
        return render_template('sponsor_campaign.html',Campaigns=campaigns,found_sponsor=found_sponsor)

@app.route("/sponsor_create_campaign",methods=['GET','POST'])
def sponsor_create_campaign():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        start_date_format = datetime.strptime(start_date, "%Y-%m-%d") 
        end_date = request.form['end_date']
        end_date_format = datetime.strptime(end_date, "%Y-%m-%d")
        budget = request.form['budget']
        goals = request.form['goals']
        visiblity = request.form['visiblity']
        genre = request.form['genre']
        sponsor_session = session['sponsor_name']
        sponsor_point = sponsor.query.filter_by(username=sponsor_session).first()
        sponsor_id = sponsor_point.sponsor_id

        new=campaign(sponsor_id=sponsor_id,campaign_name=name,description=description,goals=goals,start_date=start_date_format,end_date=end_date_format,budget=budget,visiblity=visiblity,finding_niche=genre)
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("sponsor_campaign"))
    
    return render_template('sponsor_create_campaign.html')

@app.route("/sponsor_campaign_edit",methods=['GET','POST'])
def sponsor_campaign_edit():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        start_date_format = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = request.form['end_date']
        end_date_format = datetime.strptime(end_date, "%Y-%m-%d")
        budget = request.form['budget']
        goals = request.form['goals']

        campaign_idstr =request.args.get('campaign_id')
        campaign_id = int(campaign_idstr)

        campaign_point = campaign.query.filter_by(campaign_id=campaign_id).first()

        campaign_point.campaign_name = name
        campaign_point.description = description
        campaign_point.start_date = start_date_format
        campaign_point.end_date = end_date_format
        campaign_point.budget = budget
        campaign_point.goals = goals
        db.session.commit()
        return redirect(url_for("sponsor_campaign"))
    
    else:
        campaign_idstr =request.args.get('campaign_id')
        campaign_id = int(campaign_idstr)

        found_campaign=campaign.query.filter_by(campaign_id=campaign_id).first()
        return render_template('sponsor_campaign_edit.html' ,found_campaign=found_campaign)



@app.route("/find_influencer",methods=['GET','POST'])
def find_influencer():
    if request.method == 'POST':
        influencer_name_search = request.form['influencer_name_search']
        found_influencer=influencer.query.filter_by(username=influencer_name_search,flag='no').all()
        if not found_influencer:
            flash('Influencer Does Not Exist')
            return redirect(url_for("find_influencer"))
        else:
            return render_template('find_influencer.html',found_influencer=found_influencer)
    else:
        found_influencer=influencer.query.filter_by(flag='no').all()
        return render_template('find_influencer.html',found_influencer=found_influencer)
    

@app.route("/sponsor_influencer_requests",methods=['GET','POST'])
def sponsor_influencer_requests():
    sponsor_name = session['sponsor_name']
    influencer_idstr =request.args.get('influencer_id')
    influencer_id = int(influencer_idstr)
    if request.method == 'POST':
        campaign_id_str = request.form['campaign_id']
        campaign_id = int(campaign_id_str)
        message = request.form['message']
        offer = request.form['offer']
        found_campaign = campaign.query.filter_by(campaign_id=campaign_id).first()
        sponsor_id = found_campaign.sponsor_id
        sponsor_ad_request = sponsor_request(campaign_id=campaign_id, influencer_id=influencer_id,sponsor_id=sponsor_id,message=message,amount=offer)
        db.session.add(sponsor_ad_request)
        db.session.commit()
        return redirect(url_for("find_influencer"))

    return render_template('sponsor_influencer_requests.html',influencer_id=influencer_id)



@app.route("/sponsor_assigned_campaign",methods=['GET','POST'])
def sponsor_assigned_campaign():
    if request.method == 'POST':
        sponsor_completion_approval = request.form['sponsor_completion_approval']
        completed_campaign_idstr =request.form['completed_campaign_id']
        whoes_request =request.form['whoes_request']
        completed_campaign_id = int(completed_campaign_idstr)
        if whoes_request == 'influencer':
            found_campaign = influencer_ad_request.query.filter_by(influencer_request_id=completed_campaign_id).first()
            found_campaign.status_complete_sponsor = sponsor_completion_approval 
            db.session.commit()
            
        elif whoes_request == 'sponsor':
            found_campaign = sponsor_request.query.filter_by(sponsor_request_id=completed_campaign_id).first()
            found_campaign.status_complete_sponsor = sponsor_completion_approval 
            db.session.commit()
            
    name = session['sponsor_name']
        
    # influencer ad request
    founduser=sponsor.query.filter_by(username=name).first()
    influencerRequest = db.session.query(influencer_ad_request,campaign,influencer).join(campaign,campaign.campaign_id==influencer_ad_request.campaign_id).join(influencer,influencer.influencer_id==influencer_ad_request.influencer_id)
    influencer_requests=influencerRequest.filter(influencer_ad_request.sponsor_id==founduser.sponsor_id,influencer_ad_request.sponsor_call=='Approved').all()

    # sponsor request
    sponsorRequest = db.session.query(sponsor_request,campaign,influencer).join(campaign,campaign.campaign_id==sponsor_request.campaign_id).join(influencer,influencer.influencer_id==sponsor_request.influencer_id)
    sponsor_requests=sponsorRequest.filter(sponsor_request.sponsor_id==founduser.sponsor_id,sponsor_request.influencer_call=='Approve').all()
    
    return render_template('sponsor_assigned_campaign.html',founduser=founduser,influencer_requests=influencer_requests,sponsor_requests=sponsor_requests)
    
    
@app.route("/sponsor_payment",methods=['GET','POST'])
def sponsor_payment():
    if request.method == 'POST':
        payment = request.form['payment']
        completed_campaign_idstr =request.args.get('completed_campaign_id')
        whoes_request =request.args.get('whoes_request')
        completed_campaign_id = int(completed_campaign_idstr)
        if whoes_request == 'influencer':
            found_campaign = influencer_ad_request.query.filter_by(influencer_request_id=completed_campaign_id).first()
            found_campaign.payment_sponsor = payment
            db.session.commit()
            
        elif whoes_request == 'sponsor':
            found_campaign = sponsor_request.query.filter_by(sponsor_request_id=completed_campaign_id).first()
            found_campaign.payment_sponsor = payment
            db.session.commit()

        return redirect(url_for("sponsor_assigned_campaign"))
    
    return render_template('sponsor_payment.html')

