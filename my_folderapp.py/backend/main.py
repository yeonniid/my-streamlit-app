import os
import sqlite3
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = '/workspace/data/app.db'
STARTING_CASH = 10_000_000
SYMBOLS = [
    {'symbol':'SEA-RICE','name':'동남아 쌀','price':48200,'geography':'몬순·해수면','metrics':{'온도':'28℃','강수량':'1,900mm','고도':'12m','토양 산도':'pH 6.1','용설수량':'낮음'},'summary':'몬순 비와 삼각주 관개에 민감한 주식 작물입니다.','suitable':'고온 다습하고 물을 안정적으로 댈 수 있는 저지대','risks':'엘니뇨 가뭄, 태풍, 해수면 상승'},
    {'symbol':'MED-OLIVE','name':'지중해 올리브','price':71600,'geography':'지중해성 기후','metrics':{'온도':'21℃','강수량':'540mm','고도':'280m','토양 산도':'pH 7.3','용설수량':'낮음'},'summary':'건조한 여름과 온화한 겨울에 적응한 수목 작물입니다.','suitable':'배수가 좋은 석회질 구릉과 건조한 여름','risks':'극심한 고온 건조, 산불, 병해'},
    {'symbol':'ANDES-COFFEE','name':'안데스 커피','price':89300,'geography':'고지대 기후','metrics':{'온도':'19℃','강수량':'1,500mm','고도':'1,650m','토양 산도':'pH 5.5','용설수량':'중간'},'summary':'서늘한 고도와 규칙적인 비가 향미를 만드는 작물입니다.','suitable':'서늘한 열대 고지대와 화산성 토양','risks':'엘니뇨 가뭄, 서리, 산사태'},
    {'symbol':'KARST-CEMENT','name':'카르스트 시멘트','price':35600,'geography':'석회암 지형','metrics':{'온도':'15℃','강수량':'1,100mm','고도':'420m','토양 산도':'pH 7.8','용설수량':'중간'},'summary':'석회암 매장과 채석장 접근성이 생산량을 좌우합니다.','suitable':'석회암층이 넓고 운송이 편리한 지형','risks':'싱크홀, 집중호우, 채굴 규제'},
    {'symbol':'FIORD-HYDRO','name':'피오르 수력','price':105400,'geography':'빙하 지형·수력','metrics':{'온도':'7℃','강수량':'2,300mm','고도':'600m','토양 산도':'pH 6.6','용설수량':'높음'},'summary':'강수와 빙하·적설 융수가 전력 생산을 결정합니다.','suitable':'급경사 계곡과 풍부한 강수·융수','risks':'가뭄, 빙하 후퇴, 홍수'},
    {'symbol':'NOPSO-WINE','name':'노프소 와인','price':64800,'geography':'푄 현상·포도밭','metrics':{'온도':'18℃','강수량':'620mm','고도':'350m','토양 산도':'pH 6.8','용설수량':'중간'},'summary':'건조하고 따뜻한 바람이 포도 성숙을 돕는 산지 작물입니다.','suitable':'일조량이 높고 밤낮 기온 차가 큰 사면','risks':'우박, 폭염, 가뭄'},
    {'symbol':'ARCTIC-COD','name':'북극 대구','price':57400,'geography':'한류·해빙','metrics':{'수온':'4℃','해빙 면적':'보통','수심':'180m','염분':'34‰','난류':'약함'},'summary':'차가운 바다와 해빙 가장자리의 먹이사슬에 기대는 수산 자원입니다.','suitable':'차가운 대륙붕과 안정된 해류','risks':'해수 온도 상승, 해빙 변화, 조업 제한'},
    {'symbol':'SAHEL-COTTON','name':'사헬 목화','price':42800,'geography':'반건조 기후','metrics':{'온도':'30℃','강수량':'610mm','고도':'220m','토양 산도':'pH 6.5','관개':'필요'},'summary':'짧은 우기와 물 공급의 균형이 생산량을 좌우하는 섬유 작물입니다.','suitable':'긴 일조와 배수가 좋은 평야','risks':'가뭄, 사막화, 해충'},
    {'symbol':'AMAZON-RUBBER','name':'아마존 고무','price':61200,'geography':'열대 우림','metrics':{'온도':'27℃','강수량':'2,400mm','고도':'90m','토양 산도':'pH 5.2','습도':'높음'},'summary':'고온다습한 열대 환경에서 자라는 고무나무 수액 산업입니다.','suitable':'연중 비가 많고 서리가 없는 저지대','risks':'홍수, 병해, 산림 훼손'},
    {'symbol':'PAMPA-SOY','name':'팜파 콩','price':53600,'geography':'온대 초원','metrics':{'온도':'22℃','강수량':'980mm','고도':'140m','토양 산도':'pH 6.4','토양':'비옥'},'summary':'넓고 평탄한 초원과 비옥한 토양을 활용하는 대규모 밭작물입니다.','suitable':'평탄한 평야와 계절성 강수','risks':'가뭄, 집중호우, 토양 침식'},
    {'symbol':'ATACAMA-LITH','name':'아타카마 리튬','price':124800,'geography':'염호·사막','metrics':{'온도':'17℃','강수량':'35mm','고도':'2,300m','염도':'높음','일사량':'강함'},'summary':'건조한 고원 염호의 염수 농축 조건에 의존하는 광물 자원입니다.','suitable':'강한 일사와 증발이 큰 고원 분지','risks':'물 부족, 채굴 규제, 집중호우'},
    {'symbol':'NILE-COTTON','name':'나일 목화','price':46900,'geography':'대하천 관개','metrics':{'온도':'29℃','강수량':'120mm','고도':'30m','토양':'충적토','관개':'높음'},'summary':'큰 강이 만든 비옥한 충적 평야와 관개에 의존하는 섬유 작물입니다.','suitable':'규칙적인 관개와 비옥한 하천 퇴적지','risks':'가뭄, 상류 수량 감소, 범람'},
    {'symbol':'BALTIC-WHEAT','name':'발트 밀','price':51700,'geography':'냉량 평원','metrics':{'온도':'14℃','강수량':'680mm','고도':'110m','토양':'흑토','서리':'주의'},'summary':'서늘한 여름과 넓은 평야에서 생산되는 곡물입니다.','suitable':'배수가 좋고 여름이 짧은 평원','risks':'봄철 서리, 과습, 항만 결빙'},
    {'symbol':'KALIMANTAN-PALM','name':'칼리만탄 팜','price':68400,'geography':'열대 저지대','metrics':{'온도':'28℃','강수량':'2,200mm','고도':'55m','습도':'높음','토양':'충적토'},'summary':'연중 고온다습한 저지대에서 자라는 유지 작물입니다.','suitable':'비가 고르게 오고 서리가 없는 저지대','risks':'장기 침수, 병해, 산림 훼손'},
    {'symbol':'QUEBEC-LUMBER','name':'퀘벡 목재','price':59300,'geography':'냉대 침엽수림','metrics':{'온도':'6℃','강수량':'1,050mm','고도':'410m','적설':'많음','토양':'산성'},'summary':'긴 겨울과 침엽수림 생태계에 연결된 산림 자원입니다.','suitable':'서늘하고 강수가 안정적인 산림 지대','risks':'산불, 해충, 해빙기 운송 지연'},
    {'symbol':'GANGES-JUTE','name':'갠지스 황마','price':39100,'geography':'삼각주 범람원','metrics':{'온도':'27℃','강수량':'1,700mm','고도':'18m','토양':'충적토','홍수':'주의'},'summary':'큰 강의 퇴적물과 여름철 수분에 의존하는 섬유 작물입니다.','suitable':'습윤하고 비옥한 범람원','risks':'홍수, 염수 침입, 우기 지연'},
    {'symbol':'PATAGONIA-WOOL','name':'파타고니아 양모','price':73800,'geography':'건조 고원 초지','metrics':{'온도':'9℃','강수량':'340mm','고도':'780m','풍속':'강함','초지':'보통'},'summary':'바람이 강하고 건조한 고원 초지의 목축 자원입니다.','suitable':'서늘하고 건조한 넓은 초지','risks':'가뭄, 강풍, 초지 황폐화'},
    {'symbol':'BENGAL-SHRIMP','name':'벵골 새우','price':82600,'geography':'연안 습지','metrics':{'수온':'26℃','염분':'18‰','강수량':'1,850mm','조차':'큼','해수면':'낮음'},'summary':'강물과 바닷물이 만나는 연안 습지 양식 자원입니다.','suitable':'완만한 염분 변화와 따뜻한 얕은 바다','risks':'사이클론, 염분 급변, 해수면 상승'},
    {'symbol':'MONGOL-RARE','name':'몽골 희토류','price':137600,'geography':'내륙 건조 고원','metrics':{'온도':'8℃','강수량':'260mm','고도':'1,420m','일교차':'큼','토양':'건조'},'summary':'건조한 고원 지대의 광물 매장과 물류 여건에 의존하는 자원입니다.','suitable':'강수량이 적고 접근 가능한 고원 분지','risks':'모래폭풍, 물 부족, 혹한'},
    {'symbol':'PACIFIC-KELP','name':'태평양 다시마','price':44500,'geography':'한류 연안','metrics':{'수온':'12℃','수심':'18m','염분':'33‰','파고':'보통','영양염':'높음'},'summary':'차가운 연안의 영양염과 해류에 기대는 해조 자원입니다.','suitable':'차갑고 영양염이 풍부한 얕은 바다','risks':'고수온, 적조, 거센 파랑'},
]

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS account (id INTEGER PRIMARY KEY CHECK(id=1), cash REAL NOT NULL, initial_cash REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS holdings (symbol TEXT PRIMARY KEY, quantity INTEGER NOT NULL, average_price REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL, side TEXT NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL, order_type TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, detail TEXT NOT NULL, impact_json TEXT NOT NULL, source TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS scenarios (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS game_results (id INTEGER PRIMARY KEY AUTOINCREMENT, profit REAL NOT NULL, return_rate REAL NOT NULL, duration_seconds INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
        conn.execute('INSERT OR IGNORE INTO account (id,cash,initial_cash) VALUES (1,?,?)',(STARTING_CASH,STARTING_CASH))
        conn.execute('UPDATE account SET cash=?, initial_cash=? WHERE id=1 AND initial_cash=100000000',(STARTING_CASH,STARTING_CASH))

app=FastAPI()
init_db()

class Trade(BaseModel):
    symbol:str
    side:str
    quantity:int
    price:float
    order_type:str='시장가'
class Scenario(BaseModel):
    text:str
    result:str
class Event(BaseModel):
    title:str
    detail:str
    impacts:dict
    source:str='자동 속보'
class GameResult(BaseModel):
    profit:float
    return_rate:float
    duration_seconds:int=900

@app.get('/api/health')
def health(): return {'ok':True}
@app.get('/api/catalog')
def catalog(): return SYMBOLS
@app.get('/api/state')
def state():
    with get_db() as conn:
        account=dict(conn.execute('SELECT cash,initial_cash FROM account WHERE id=1').fetchone())
        holdings=[dict(r) for r in conn.execute('SELECT * FROM holdings').fetchall()]
        trades=[dict(r) for r in conn.execute('SELECT * FROM trades ORDER BY id DESC LIMIT 20').fetchall()]
        events=[dict(r) for r in conn.execute('SELECT * FROM events ORDER BY id DESC LIMIT 12').fetchall()]
        scenarios=[dict(r) for r in conn.execute('SELECT * FROM scenarios ORDER BY id DESC LIMIT 10').fetchall()]
        games=[dict(r) for r in conn.execute('SELECT * FROM game_results ORDER BY id DESC LIMIT 1').fetchall()]
    return {'account':account,'holdings':holdings,'trades':trades,'events':events,'scenarios':scenarios,'last_game':games[0] if games else None}
@app.post('/api/trade')
def trade(data:Trade):
    if data.symbol not in [s['symbol'] for s in SYMBOLS] or data.side not in ('buy','sell','short','cover') or data.quantity < 1 or data.price <= 0:
        raise HTTPException(400,'주문 정보를 확인해 주세요.')
    with get_db() as conn:
        cash=conn.execute('SELECT cash FROM account WHERE id=1').fetchone()['cash']
        row=conn.execute('SELECT quantity,average_price FROM holdings WHERE symbol=?',(data.symbol,)).fetchone()
        qty=row['quantity'] if row else 0; avg=row['average_price'] if row else 0; total=data.price*data.quantity
        if data.side=='buy':
            if qty < 0: raise HTTPException(400,'공매도 잔량은 먼저 상환해 주세요.')
            if cash < total: raise HTTPException(400,'가상 현금이 부족해요. 수량을 줄여 주세요.')
            new_qty=qty+data.quantity; new_avg=((qty*avg)+total)/new_qty
            conn.execute('UPDATE account SET cash=cash-? WHERE id=1',(total,))
        elif data.side=='sell':
            if qty < data.quantity: raise HTTPException(400,'보유 수량이 부족해요. 현재 보유량을 확인해 주세요.')
            new_qty=qty-data.quantity; new_avg=avg
            conn.execute('UPDATE account SET cash=cash+? WHERE id=1',(total,))
        elif data.side=='short':
            if qty > 0: raise HTTPException(400,'매수 보유분은 먼저 매도해 주세요.')
            new_qty=qty-data.quantity; new_avg=((abs(qty)*avg)+total)/abs(new_qty)
            conn.execute('UPDATE account SET cash=cash+? WHERE id=1',(total,))
        else:
            if qty >= 0 or abs(qty) < data.quantity: raise HTTPException(400,'상환할 공매도 수량이 부족해요.')
            if cash < total: raise HTTPException(400,'가상 현금이 부족해 상환할 수 없어요.')
            new_qty=qty+data.quantity; new_avg=avg
            conn.execute('UPDATE account SET cash=cash-? WHERE id=1',(total,))
        if new_qty==0: conn.execute('DELETE FROM holdings WHERE symbol=?',(data.symbol,))
        else: conn.execute('INSERT INTO holdings(symbol,quantity,average_price) VALUES(?,?,?) ON CONFLICT(symbol) DO UPDATE SET quantity=excluded.quantity,average_price=excluded.average_price',(data.symbol,new_qty,new_avg))
        conn.execute('INSERT INTO trades(symbol,side,quantity,price,order_type) VALUES(?,?,?,?,?)',(data.symbol,data.side,data.quantity,data.price,data.order_type))
    labels={'buy':'매수','sell':'매도','short':'공매도','cover':'상환'}
    return {'message':f"{data.symbol} {data.quantity:,}주 {labels[data.side]}가 완료됐어요."}
@app.post('/api/events')
def add_event(data:Event):
    with get_db() as conn: conn.execute('INSERT INTO events(title,detail,impact_json,source) VALUES(?,?,?,?)',(data.title,data.detail,json.dumps(data.impacts,ensure_ascii=False),data.source))
    return {'ok':True}
@app.post('/api/scenarios')
def scenario(data:Scenario):
    with get_db() as conn: conn.execute('INSERT INTO scenarios(text,result) VALUES(?,?)',(data.text,data.result))
    return {'ok':True}
@app.post('/api/games')
def save_game(data:GameResult):
    with get_db() as conn: conn.execute('INSERT INTO game_results(profit,return_rate,duration_seconds) VALUES(?,?,?)',(data.profit,data.return_rate,data.duration_seconds))
    return {'ok':True}
