from fastapi import FastAPI, Request , Form
from fastapi.templating import Jinja2Templates
import uvicorn
from typing_extensions  import Annotated 
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine

# 데이터베이스 연결 셋팅
                            # 'DB이름://아이디:비밀번호@IP:포트/데이터베이스'
db_connection = create_engine('mysql://coffee:1234@175.106.96.251:3306/coffee')
print(db_connection)

# FASTAPI 프론트파일들 즉, html이 있는 폴더를 지칭
templates = Jinja2Templates(directory="templates")

# FASTAPI 프레임워크를 생성
app = FastAPI()

# static = 이미지파일들 어느폴더에 있냐 라고 알려주는것
app.mount("/static", StaticFiles(directory="static"), name="static")

# 웹주소를 쳤을때 아래 함수가 실행, main.html을 웹화면에 랜더링
@app.get("/")
def test(request: Request):
    print(request)
    return templates.TemplateResponse("main.html", {'request': request})

# 로그인 버튼을 눌렀을때, 로그인 화면으로 넘어가게끔하는 함수.
@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {'request': request})

# 웹화면에서 아이디랑 비밀번호를 치고 사용자가 로그인이 버튼을 눌렀을때 실행되는 함수, 화분보여줘야하는데 <- 포인트 조회 <- SQL
@app.post("/loginpost")
def loginpost(request: Request, username: str = Form(...), password: str = Form(...)):
    # 아이디랑 비밀번호가 데이터베이스에 진짜 저장되어있는지 확인
    query = db_connection.execute("select * from user where user_id = '{}' and user_pwd like '{}'".format(username, password))
    result_db = query.fetchall()

    # 조회된게 있다면 result_db변수에 회원정보가 담겨지는데 회원정보가 있으면 내용물이있겠고 (길이가1)
    # 조회된게 없다면 내용물이 없으니까 (길이가 0)
    if len(result_db) >= 1:
        print(list(result_db)[0][4])
        return templates.TemplateResponse("result.html", {'request': request, 'username': username, 'score': list(result_db)[0][4]})
    else:
        return  {"message": "ID or PWD error" }


# 회원가입 버튼을 눌렀을때, 회원가입창 signup.html 넘어가는코드
@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {'request': request})

# 사용자가 signup.html 에서 각종정보들을 입력하고 회원가입 버튼을 눌렀을때 
@app.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    try:
        # 데이터베이스에서 사용자의 정보들을 추가한다.
        db_connection.execute(f"insert into user(user_id, user_pwd, user_email, point) values('{username}', '{password}', '{email}',0);")
    except:
        # 사용자가 작성 안한 정보가 있다면 메세지를 웹화면에서 띄움
        return {"message": "username or password or email NULL" }
    # 에러가 없이 == 사용자가 다 문제없이 데이터베이스에 추가 되었다면,
    # login.html 로그인 화면으로 넘어감.
    return templates.TemplateResponse("login.html", {'request': request,'name':username})


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)