from  flask import Flask,session,render_template ,request
import mysql.connector
import base64

app = Flask(__name__)
app.secret_key="5878"

@app.route("/")
def index():

    return render_template("home.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin_login_check",methods =["GET", "POST"])
def admin_login_check():
    uid = request.form.get("uid")
    pwd = request.form.get("pswd")

    if uid=="admin" and pwd=="admin":
        return render_template("adminhome.html")
    else:
        return render_template("admin.html",msg="Invalid Credentials")

    return ""

@app.route("/ahome")
def ahome():
    return render_template("adminhome.html")

@app.route("/view_students")
def view_students():
    con,cur = database()
    sql = "select * from registration where status='wait' "
    cur.execute(sql)
    vals = cur.fetchall()
    #picture = vals[6]
    '''for vals in vals:
        picture = vals[6]
        data = base64.b64decode(picture)
        with open("..\VIT\static\picture.jpg", 'wb') as f:
            f.write(data)'''
    return render_template("view_students.html",vals=vals)

@app.route("/view_photo/<sno>")
def view_photo(sno):
    con,cur = database()
    qry = "select image from registration where student_id='"+sno+"'"
    cur.execute(qry)
    image=cur.fetchone()[0]
    return render_template("view_idcard.html",image=image)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_store",methods=["post","get"])
def register_store():
    name = request.form['name']
    srn = request.form['rno']
    brnh = request.form['brnch']
    email = request.form['email']
    pwd = request.form['pswd']
    mno = request.form['mno']
    image = request.files['file']

    con, cur = database()
    sql = "select count(*) from registration where student_id='" + srn + "' or student_email='" + email + "'"
    cur.execute(sql)
    res = cur.fetchone()[0]
    if res > 0:
        return render_template("register.html", msg=True)
    else:
        qry = "insert into registration(student_name,student_id,branch,student_email,password,mobile_number,image,status) values  (%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (name, srn, brnh, email, pwd, mno, image.filename,"wait")
        cur.execute(qry, values)
        con.commit()
        return render_template("login.html", msg="Registered Successfully..! Login Here.")

    return ""

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_check",methods=["post","get"])
def login_check():
    semail = request.form["semail"]
    pswd = request.form["pswd"]
    con, cur = database()
    qry = "SELECT * FROM registration  WHERE student_email='%s' AND password='%s'"
    cur.execute(qry % (semail, pswd))
    res = cur.fetchone()
    if res:
        session["semail"] = semail

        return render_template("student_home.html")

    else:
        return render_template("login.html", msg2="invalid credentials")

@app.route("/shome")
def shome():
    semail = session["semail"]
    return render_template("student_home.html")

@app.route("/add_items")
def add_items():
    return render_template("add_items.html")

@app.route("/item_adding",methods=["POST","GET"])
def item_adding():
    #filenames=[]
    #filenames.clear()
    category = request.form['category']
    pnm = request.form['pname']
    cost = request.form['price']
    #brand = request.form['brand']
    desc = request.form['description']
    #Get the list of files from webpage
    files = request.files["file"]
    semail = session["semail"]
    con, cur = database()
    qry = "insert into products_store (category,product_name,price,description,image,student_email) values  ('%s','%s','%s','%s','%s','%s')"
    cur.execute(qry % (category,pnm, cost,desc,files.filename,semail))
    con.commit()
    return render_template("student_home.html", msg="product added Successfully..! ")

@app.route("/view_items")
def view_items():
    semail = session["semail"]
    con,cur=database()
    qry="select * from products_store where student_email='"+semail +"' "
    cur.execute(qry)
    items=cur.fetchall()
    print(items)
    return render_template("view_items.html",items=items)

@app.route("/accept/<student_id>")
def accept(student_id):
    con, cur = database()
    sql = "update registration set status='Approved'  where student_id='" + student_id + "'"
    cur.execute(sql)
    con.commit()
    qry = "select * from registration where status='wait'"
    cur.execute(qry)
    vals = cur.fetchall()
    return render_template("view_students.html", vals=vals)

@app.route("/reject/<student_id>")
def reject(student_id):
    con, cur = database()
    sql = "update registration set status='Rejected'  where student_id='" + student_id + "'"
    cur.execute(sql)
    con.commit()
    sql = "delete from registration where student_id='" + student_id + "' and  status='Rejected'"
    cur.execute(sql)
    con.commit()
    qry = "select * from registration where status='wait'"
    cur.execute(qry)
    vals = cur.fetchall()
    return render_template("view_students.html", vals=vals)

@app.route("/shop")
def shop():
    semail = session["semail"]
    con,cur = database()
    qry= "select * from products_store where student_email!='"+semail+"'"
    cur.execute(qry)
    items=cur.fetchall()
    return render_template("shop.html",items=items)

@app.route("/view/<id>")
def view(id):
    semail = session["semail"]
    con,cur= database()
    qry = "select * from products_store where product_id='"+id+"'"
    cur.execute(qry)
    items=cur.fetchone()

    return render_template("view.html",items=items,semail=semail)

@app.route("/Like/<email>/<id>/<owner_email>")
def Like(email,id,owner_email):
    con,cur = database()
    qry = "insert into wishlist (product_id,student_email,owner_email) values('%s','%s','%s' )"
    cur.execute(qry %(id,email,owner_email))
    con.commit()

    semail = session["semail"]
    con, cur = database()
    qry = "select * from products_store where student_email!='" + semail + "'"
    cur.execute(qry)
    items = cur.fetchall()
    return render_template("shop.html", items=items)
    #return render_template("student_home.html")

@app.route("/wishlist")
def wishlist():
    semail = session["semail"]
    con,cur = database()
    qry = "select * from wishlist where owner_email='"+semail+"'"
    cur.execute(qry)
    res = cur.fetchall()
    print("res",res)
    if len(res)==0:
        return render_template("whishlist.html",msg="no data")
        pass
    else:
        wishlist=[]
        list=[]
        for vals in res:
            pid=vals[0]
            #print(pid)
            stu_email=vals[1]
            qry2="select * from products_store where  product_id='"+pid+"'"
            cur.execute(qry2)
            res2=cur.fetchall()
            pnm=res2[0][2]
            image=res2[0][6]

            list.append([pid,pnm,image,stu_email])

        #wishlist.append(list)
        #print("wishlist",wishlist)
        return render_template("whishlist.html",wishlist=list)
    return""

@app.route("/wishlist2")
def wishlist2():

    semail = session["semail"]
    con,cur = database()
    qry = "select * from wishlist where student_email='"+semail+"'"
    cur.execute(qry)
    res = cur.fetchall()
    print("res",res)
    if len(res)==0:
        return render_template("whishlist2.html",msg="no data")
        pass
    else:

        list = []
        for vals in res:
            pid=vals[0]
            print(pid)
            owner_email=vals[2]
            qry2="select * from products_store where  product_id='"+pid+"'"
            cur.execute(qry2)
            res2=cur.fetchall()
            print("res2",res2)
            pnm=res2[0][2]
            image=res2[0][6]

            list.append([pid, pnm, image, owner_email])
            print("list",list)

        return render_template("whishlist2.html", wishlist=list)
    return ""

@app.route("/cart/<id>")
def cart(id):
    semail = session["semail"]
    con,cur = database()
    qry="select * from products_store where product_id='"+id+"'"
    cur.execute(qry)
    items=cur.fetchall()
    for item in items:
        id=item[0]
        cat=item[1]
        pnm=item[2]
        pcst=item[3]
        #smail=item[5]
        image=item[6]
    print("cart items",items)

    sql="insert into cart(product_id,category,product_name,product_cost,student_email,product_image) values ('%s','%s','%s','%s','%s','%s')"
    cur.execute(sql % (id,cat,pnm,pcst,semail,image))
    con.commit()

    qry = "select * from products_store where student_email!='" + semail + "'"
    cur.execute(qry)
    items = cur.fetchall()
    return render_template("shop.html", items=items,msg="added")



@app.route("/Chat_Owner/<owner_email>")
def Chat_Owner(owner_email):
    con, cur = database()
    semail = session["semail"]

    eqry = "select count(*) from msgs2 where receiver_email='" + owner_email + "' and sender_email='" + semail + "'"
    cur.execute(eqry)
    res = cur.fetchone()[0]
    if res > 0:
        pass
    else:
        sql = "insert into msgs2(receiver_email,sender_email) values ('%s','%s') "
        cur.execute(sql % (owner_email,semail))
        con.commit()

    qry = "select * from msgs  where chatof='" +semail  + "" +owner_email  + "'  order by sno ";
    cur.execute(qry)
    chatrec = cur.fetchall()
    return render_template("chat.html", semail=semail, chatrec=chatrec, owner_email=owner_email)

@app.route("/schatbot2",methods=["get","post"])
def schatbot2():
    s_email = request.form.get('s_email')
    msg = request.form.get('text')
    semail = session["semail"]
    con, cur = database()
    qry="insert into msgs(msg, user_, time_, chatof, status) values ('%s','%s',now(),'%s','%s')"
    cur.execute(qry % (msg, semail,s_email+semail, "new"))
    con.commit()
    qry = "select * from msgs  where chatof='" +s_email + "" +  semail + "'  order by sno ";
    cur.execute(qry)
    chatrec = cur.fetchall()
    return render_template("schat.html",s_email=s_email,chatrec=chatrec,owner_email=semail)

@app.route("/view_chat")
def view_chat():
    semail = session["semail"]
    con, cur = database()
    qry = "select * from msgs2  where receiver_email='"+semail+"' "
    cur.execute(qry)
    res = cur.fetchall()
    return render_template("view_chat.html",values=res)

@app.route("/chat/<s_email>")
def chat(s_email):
    owner_email = session["semail"]
    con, cur = database()
    qry = "select * from msgs  where chatof='" + s_email + "" + owner_email + "'  order by sno ";
    cur.execute(qry)
    chatrec = cur.fetchall()
    return render_template("schat.html", s_email=s_email, chatrec=chatrec, owner_email=owner_email)

@app.route("/chatbot2",methods=["get","post"])
def chatbot2():
    owner_email = request.form.get('owner_email')
    #print("s_email",s_email)
    msg = request.form.get('text')

    semail = session["semail"]
    print("semail",semail)
    con, cur = database()
    qry="insert into msgs(msg, user_, time_, chatof, status) values ('%s','%s',now(),'%s','%s')"
    cur.execute(qry % (msg, semail, semail+owner_email,"new"))
    con.commit()
    qry = "select * from msgs  where chatof='" + semail + "" + owner_email + "'  order by sno ";
    cur.execute(qry)
    chatrec = cur.fetchall()
    return render_template("chat.html",owner_email=owner_email,chatrec=chatrec,semail=semail)

@app.route("/view_cart")
def view_cart():
    semail = session["semail"]
    con,cur = database()
    qry="select * from cart where student_email='"+semail+"'"
    cur.execute(qry)
    items=cur.fetchall()
    totcost = 0
    #shipcost = 45
    for values in items:
        totcost = totcost + int(values[4])
    main = totcost
    return render_template("cart.html",items=items, fruits=items,cost=totcost,total=main)

@app.route('/remove/<sno>')  # decorator drfines the
def remove(sno):

    con,cur=database()
    dq = "DELETE FROM cart  WHERE sno='"+sno+"'"
    cur.execute(dq)
    con.commit()

    semail = session["semail"]
    qry = "select * from cart where student_email='" + semail + "'"
    cur.execute(qry)
    items = cur.fetchall()
    totcost = 0
    #shipcost = 45
    for values in items:
        totcost = totcost + int(values[4])
    main = totcost
    return render_template("cart.html", items=items, fruits=items, cost=totcost, total=main,msg="removed")

@app.route("/place_order")
def place_order():
    return render_template("place_order.html")

@app.route("/payment",methods=["post","get"])
def payment():
    pmthd=request.form["pmthd"]
    upi=request.form["upi"]

    semail = session["semail"]
    con, cur = database()
    cur.execute("select *from cart where student_email='"+semail+"' ")
    res = cur.fetchall()
    for records in res:
        iq = ("insert into order_table(product_id,category,product_name,product_cost,product_image,student_email) values('%s','%s','%s','%s','%s','%s')")
        cur.execute(iq % (records[1], records[2], records[3], records[4],records[6],records[5]))
        con.commit()

    dq = " DELETE  from cart where student_email='"+semail+"' "
    cur.execute(dq)
    con.commit()
    return render_template("student_home.html",msg2="placed")

def database():
    con=mysql.connector.connect(host="127.0.0.1",user="root",password="root",database="student_treasures_exchange")
    cur=con.cursor()
    return con,cur


@app.route("/orders")
def orders():
    semail = session["semail"]
    con, cur = database()
    cur.execute("select * from order_table where student_email='"+semail+"'")
    res = cur.fetchall()
    return render_template("order.html", orders=res)

if __name__=='__main__':
    app.run(debug=True)