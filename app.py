import os, re, base64, io, math, json, time
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None
try:
    import plotly.graph_objects as go
except Exception:
    go = None
try:
    import requests
except Exception:
    requests = None
try:
    from PIL import Image
except Exception:
    Image = None
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
except Exception:
    Workbook = None
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except Exception:
    SimpleDocTemplate = None
try:
    from st_img_pastebutton import paste as paste_image
except Exception:
    paste_image = None

BASE=Path(__file__).resolve().parent
LOGO=BASE/'vs_flow_logo.png'
APP='VS FLOW SUPER COMPUTER'
VERSION='V10.0 — SUPER COMPUTER FINAL'
AUTHOR='VAIBHAV SHIRSAT'
MTFS=['1W','1D','4H','1H','30M','15M','5M','1M']
WEIGHTS={'1W':15,'1D':20,'4H':20,'1H':15,'30M':10,'15M':8,'5M':10,'1M':2}

POPULAR={
'NIFTY':'^NSEI','NIFTY50':'^NSEI','BANKNIFTY':'^NSEBANK','SENSEX':'^BSESN','INDIAVIX':'^INDIAVIX',
'SPX':'^GSPC','S&P500':'^GSPC','NASDAQ':'^IXIC','DOW':'^DJI','DAX':'^GDAXI','FTSE':'^FTSE','NIKKEI':'^N225','HANGSENG':'^HSI','CAC40':'^FCHI','ASX200':'^AXJO','KOSPI':'^KS11','SSE':'000001.SS','CSI300':'000300.SS','NIFTYIT':'^CNXIT','NIFTYBANK':'^NSEBANK',
'BTC':'BTC-USD','BTCUSD':'BTC-USD','ETH':'ETH-USD','SOL':'SOL-USD','XRP':'XRP-USD','BNB':'BNB-USD','DOGE':'DOGE-USD','ADA':'ADA-USD','AVAX':'AVAX-USD','LINK':'LINK-USD','DOT':'DOT-USD','TRX':'TRX-USD',
'GOLD':'GC=F','SILVER':'SI=F','CRUDE':'CL=F','WTI':'CL=F','NATGAS':'NG=F','COPPER':'HG=F','PLATINUM':'PL=F','PALLADIUM':'PA=F','USDINR':'INR=X','EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'JPY=X'
}
INDIA100='''RELIANCE TCS HDFCBANK ICICIBANK BHARTIARTL INFY SBIN LT ITC HINDUNILVR AXISBANK KOTAKBANK M&M MARUTI SUNPHARMA HCLTECH BAJFINANCE TITAN ULTRACEMCO ADANIENT ADANIPORTS NTPC ONGC POWERGRID JSWSTEEL TATASTEEL WIPRO NESTLEIND ASIANPAINT TECHM TATAMOTORS EICHERMOT COALINDIA BAJAJFINSV GRASIM HINDALCO DIVISLAB DRREDDY CIPLA APOLLOHOSP HEROMOTOCO BPCL BRITANNIA TATACONSUM INDUSINDBK SHRIRAMFIN BEL TRENT ZOMATO JIOFIN IRCTC PIDILITIND DLF LODHA SIEMENS ABB VEDL HAL BHEL IOC GAIL BANKBARODA CANBK PNB UNIONBANK IDFCFIRSTB INDIAMART DMART TVSMOTOR BOSCHLTD MOTHERSON VBL DABUR MARICO GODREJCP COLPAL SBICARD ICICIPRULI CHOLAFIN MUTHOOTFIN OFSS LTIM LTTS PERSISTENT MPHASIS COFORGE CUMMINSIND VOLTAS AMBER APLAPOLLO AUROPHARMA LUPIN TORNTPHARM BIOCON SRF PIIND ASTRAL CONCOR NHPC DIXON'''.split()
GLOBAL_STOCKS=list(dict.fromkeys('''AAPL MSFT NVDA AMZN GOOGL META AVGO TSLA BRK-B JPM WMT ORCL COST NFLX AMD CRM INTC QCOM MU TXN AMAT NOW ADBE INTU ISRG LLY NVO UNH JNJ PG KO PEP XOM CVX COP CAT GE BA RTX HON UBER SHOP PLTR BABA TSM ASML SAP SONY TM NVS RY HSBC TD BHP RIO SHEL V MA CSCO IBM GEHC LMT GS BAC PFE MRK ABBV MCD DIS VZ T ARM SMCI SNOW'''.split()))
GLOBAL_INDICES=list(dict.fromkeys(['^GSPC','^IXIC','^DJI','^RUT','^GDAXI','^FTSE','^FCHI','^N225','^HSI','^KS11','^AXJO','^STOXX50E','^BSESN','^NSEI','^NSEBANK','^CNXIT','^INDIAVIX','^STI','^NZ50','^GSPTSE','^BVSP','^MXX','000001.SS','000300.SS','^TWII','^TA125.TA','^JKSE','^KLSE','^SET.BK']))
CRYPTO=['BTC-USD','ETH-USD','SOL-USD','BNB-USD','XRP-USD','DOGE-USD','ADA-USD','AVAX-USD','LINK-USD','DOT-USD','TRX-USD','SHIB-USD','LTC-USD','BCH-USD','UNI-USD','ATOM-USD','NEAR-USD','APT-USD','SUI-USD','ICP-USD','FIL-USD','ETC-USD','HBAR-USD','XLM-USD','MATIC-USD']
COMMODITIES=['GC=F','SI=F','CL=F','BZ=F','NG=F','HG=F','PL=F','PA=F','ZC=F','ZS=F','ZW=F','KC=F','CC=F','CT=F','LE=F','HE=F']

st.set_page_config(page_title=f'{APP} • {AUTHOR}',page_icon='⚡',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
:root{--bg:#070807;--panel:#111311;--panel2:#151815;--line:#2b302b;--gold:#c9a96a;--gold2:#e5c98b;--green:#6fcf97;--red:#d77a7a;--cyan:#9fb8ad;--muted:#8e958d;--white:#f2eee5;--ink:#0a0b0a}
.stApp{background:radial-gradient(circle at 78% 0%,rgba(201,169,106,.075),transparent 24%),radial-gradient(circle at 12% 10%,rgba(111,207,151,.035),transparent 22%),linear-gradient(180deg,#080908 0%,#0b0d0b 48%,#070807 100%);color:var(--white)}
.block-container{max-width:1900px;padding:1.1rem 1rem 2.2rem!important}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0c0a,#0d100d 55%,#090a09)!important;border-right:1px solid #252a25!important}section[data-testid="stSidebar"]>div{background:transparent!important}
.hero{min-height:122px;box-sizing:border-box;border:1px solid #4a402c;border-radius:18px;padding:10px 18px;background:linear-gradient(100deg,rgba(14,16,14,.98),rgba(25,27,23,.96));box-shadow:0 12px 38px rgba(0,0,0,.28),inset 0 1px rgba(255,255,255,.035);margin:0 0 12px;overflow:visible}.hero-row{min-height:98px;display:flex;align-items:center;justify-content:space-between;gap:20px}.hero-left{display:flex;align-items:center;gap:16px;min-width:0}.hero-logo{width:90px;height:90px;flex:0 0 82px;border-radius:50%;object-fit:cover;border:1px solid #9e7e3f;box-shadow:0 0 22px rgba(201,169,106,.12)}.brand{font-size:38px;font-weight:1000;letter-spacing:-1.5px;background:linear-gradient(90deg,#f5ead1,#d7b873,#a9894d);-webkit-background-clip:text;color:transparent;line-height:1.05;white-space:nowrap}.sub{color:#a8aea6;font-size:10px;letter-spacing:3px;margin-top:6px;white-space:nowrap}.owner{text-align:right;white-space:nowrap}.owner b{font-size:17px;color:#dec48c}.owner span{display:block;color:#7f877f;font-size:9px;letter-spacing:2px;margin-top:5px}
.stButton button{background:linear-gradient(180deg,#1a1f1a,#101310)!important;border:1px solid #394039!important;color:#eee9dd!important;border-radius:9px!important;font-weight:800!important;box-shadow:inset 0 1px rgba(255,255,255,.025)!important}.stButton button:hover{border-color:var(--gold)!important;box-shadow:0 0 18px rgba(201,169,106,.12)!important;color:#f6e8c6!important}.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div{background:#101310!important;color:#eee9dd!important;border:1px solid #343a34!important;border-radius:8px!important}.searchbar{border:1px solid #51462f;border-radius:18px;padding:7px;background:#111310}
.ticker{background:linear-gradient(145deg,#151815,#0f120f);border:1px solid #2f352f;border-radius:9px;padding:8px 10px;min-height:78px;box-shadow:0 8px 18px rgba(0,0,0,.14)}.ticker .name{font-size:10px;color:#aaafa8;font-weight:800}.ticker .px{font-size:17px;font-weight:900;margin-top:3px}.up{color:var(--green)}.down{color:var(--red)}.section-title{font-size:18px;font-weight:950;letter-spacing:.4px;margin:12px 0 6px;color:#eee9df}.panel{background:linear-gradient(145deg,rgba(19,22,19,.98),rgba(12,14,12,.98));border:1px solid #303630;border-radius:14px;padding:12px;box-shadow:inset 0 1px rgba(255,255,255,.025),0 12px 28px rgba(0,0,0,.22)}
.hero-market{min-height:360px;background:radial-gradient(circle at 50% 45%,rgba(201,169,106,.08),transparent 22%),radial-gradient(circle at 35% 50%,rgba(111,207,151,.035),transparent 28%),linear-gradient(145deg,#111411,#090b09 70%);border:1px solid #3c3a2f;border-radius:14px;padding:12px;text-align:center;overflow:hidden}.hero-market img{width:min(330px,62%);opacity:.94;filter:drop-shadow(0 0 20px rgba(201,169,106,.12));margin-top:8px}.hero-market h2{margin:0;color:#f2eee5;font-size:22px;letter-spacing:2px}.hero-market p{color:#969d95;font-size:10px;letter-spacing:2px;margin:5px 0}.goldline{color:#d8bd7d;font-size:11px;letter-spacing:2px;margin-top:4px}.metric-card{background:linear-gradient(145deg,#171a17,#101210);border:1px solid #303630;border-radius:10px;padding:10px}.metric-card .k{font-size:9px;color:#929990;text-transform:uppercase;letter-spacing:1px}.metric-card .v{font-size:19px;font-weight:950;margin-top:3px}.small{font-size:10px;color:#8f978e}.gold{color:#d9bc79}.green{color:#72ce98}.red{color:#d97f7f}.cyan{color:#b7c9bf}.setup-row{display:grid;grid-template-columns:1.1fr .7fr 1.1fr .7fr .5fr;gap:6px;padding:7px 8px;border-bottom:1px solid #272c27;font-size:10px;align-items:center}.setup-row.head{color:#8f978e;font-weight:900}.badge{padding:3px 7px;border-radius:5px;font-weight:900;font-size:10px;display:inline-block}.buy{background:rgba(111,207,151,.10);color:#78d49c;border:1px solid rgba(111,207,151,.24)}.sell{background:rgba(215,122,122,.10);color:#df8787;border:1px solid rgba(215,122,122,.24)}.score{background:#294333;color:#a8e0bd;border-radius:5px;padding:3px 7px;font-weight:900;text-align:center}.regime-big{font-size:22px;font-weight:1000;margin:6px 0 12px}.bullet{font-size:12px;margin:9px 0;color:#c8cdc6}.icon-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:8px}.icon-item{border:1px solid #303730;border-radius:10px;padding:10px;text-align:center;background:#101310}.icon-item .i{font-size:22px}.icon-item b{font-size:10px;display:block;margin-top:5px}.icon-item span{font-size:8px;color:#8b938a}div[data-testid="stDataFrame"]{border:1px solid #303630;border-radius:10px;overflow:hidden}div[data-testid="stMetric"]{background:#121512;border:1px solid #2e342e;border-radius:10px;padding:8px}div[data-testid="stMetricLabel"]{color:#929990!important}div[data-testid="stMetricValue"]{color:#eee9df!important}footer{visibility:hidden}
@media(max-width:1000px){.hero{min-height:125px}.hero-row{align-items:center}.brand{font-size:28px}.hero-logo{width:70px;height:70px;flex-basis:70px}.owner b{font-size:14px}.icon-grid{grid-template-columns:repeat(2,1fr)}}

.super-hero{border:1px solid #6a5830;border-radius:20px;padding:20px 22px;background:linear-gradient(120deg,#0c0d0c 0%,#181712 45%,#0c0d0c 100%);box-shadow:0 20px 55px rgba(0,0,0,.35),inset 0 1px rgba(255,255,255,.04);margin-bottom:14px}.super-hero h1{font-size:34px;margin:0;background:linear-gradient(90deg,#f7edda,#d8b76c,#f1dfb2);-webkit-background-clip:text;color:transparent}.super-hero p{color:#a9a99f;letter-spacing:1.6px;font-size:11px;margin:7px 0 0}.gold-rule{height:2px;background:linear-gradient(90deg,#b58a3d,#f1d78e,#806126);border-radius:4px;margin-top:14px}.command-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.command-card{border:1px solid #34372f;border-radius:13px;padding:13px;background:linear-gradient(145deg,#171815,#0e100e);min-height:92px}.command-card .label{font-size:9px;color:#94988f;letter-spacing:1.2px}.command-card .value{font-size:21px;font-weight:950;margin-top:5px}.command-card .subv{font-size:9px;color:#777e76;margin-top:4px}.watch-card{border-left:3px solid #a98a50;padding:9px 12px;background:#11130f;border-radius:8px;margin-bottom:6px}.status-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#74cf98;margin-right:5px}.muted{color:#80877e}.gold-border{border:1px solid #5b4b2e!important}
@media(max-width:1100px){.command-grid{grid-template-columns:repeat(2,1fr)}}
</style>''',unsafe_allow_html=True)

def resolve(q,market='Auto'):
    q=(q or '').strip().upper()
    if q in POPULAR:return POPULAR[q]
    if q.endswith(('.NS','.BO','.L','.DE','.HK','.TO','.T','.AX')) or '=' in q or q.startswith('^') or '-' in q:return q
    if market=='India':return q+'.NS'
    if market=='Crypto':return q+'-USD'
    return q

@st.cache_data(ttl=90,show_spinner=False)
def fetch(symbol,period='1y',interval='1d'):
    if yf is None:return pd.DataFrame()
    try:
        d=yf.download(symbol,period=period,interval=interval,auto_adjust=False,progress=False,threads=False)
        if d is None or d.empty:return pd.DataFrame()
        if isinstance(d.columns,pd.MultiIndex): d=d.droplevel(1,axis=1)
        d.columns=[str(x).title() for x in d.columns]
        return d.dropna(how='all')
    except Exception:return pd.DataFrame()

@st.cache_data(ttl=120,show_spinner=False)
def fetch_batch(symbols,period='3mo',interval='1d'):
    if yf is None or not symbols:return {}
    try:
        d=yf.download(symbols,period=period,interval=interval,auto_adjust=False,progress=False,threads=True,group_by='ticker')
        out={}
        if isinstance(d.columns,pd.MultiIndex):
            for sym in symbols:
                if sym in d.columns.get_level_values(0):
                    x=d[sym].copy();x.columns=[str(c).title() for c in x.columns];out[sym]=x.dropna(how='all')
        else:
            x=d.copy();x.columns=[str(c).title() for c in x.columns];out[symbols[0]]=x.dropna(how='all')
        return out
    except Exception:return {}

def rsi(s,n=14):
    d=s.diff();up=d.clip(lower=0);dn=-d.clip(upper=0);rs=up.ewm(alpha=1/n,adjust=False).mean()/dn.ewm(alpha=1/n,adjust=False).mean().replace(0,np.nan);return 100-100/(1+rs)

def enrich(d):
    x=d.copy()
    if x.empty:return x
    x['EMA18']=x.Close.ewm(span=18,adjust=False).mean();x['EMA20']=x.Close.ewm(span=20,adjust=False).mean();x['EMA50']=x.Close.ewm(span=50,adjust=False).mean();x['EMA200']=x.Close.ewm(span=200,adjust=False).mean();x['RSI']=rsi(x.Close)
    tr=pd.concat([x.High-x.Low,(x.High-x.Close.shift()).abs(),(x.Low-x.Close.shift()).abs()],axis=1).max(axis=1);x['ATR']=tr.rolling(14).mean();x['VMA20']=x.Volume.rolling(20).mean() if 'Volume' in x else np.nan;x['VOLR']=x.Volume/x.VMA20 if 'Volume' in x else np.nan
    return x

def structure(d):
    if d.empty:return {'bias':'NO DATA','score':0}
    x=enrich(d);c=float(x.Close.iloc[-1]);vals=[c>x.EMA18.iloc[-1],x.EMA18.iloc[-1]>x.EMA50.iloc[-1],x.EMA50.iloc[-1]>x.EMA200.iloc[-1],c>x.Close.iloc[-10] if len(x)>10 else False,c>x.Close.iloc[-20] if len(x)>20 else False];sc=int(sum(vals))
    return {'bias':'BULLISH TREND' if sc>=4 else 'BEARISH TREND' if sc<=1 else 'MIXED / RANGE','score':sc,'close':c,'ema18':float(x.EMA18.iloc[-1]),'ema50':float(x.EMA50.iloc[-1]),'ema200':float(x.EMA200.iloc[-1]),'rsi':float(x.RSI.iloc[-1]),'atr':float(x.ATR.iloc[-1])}

def liquidity(d):
    if len(d)<20:return 'NO CLEAR SWEEP'
    x=d.tail(31);last=x.iloc[-1];ph=x.High.iloc[:-1].max();pl=x.Low.iloc[:-1].min()
    if last.High>ph and last.Close<ph:return 'BUY-SIDE SWEEP'
    if last.Low<pl and last.Close>pl:return 'SELL-SIDE SWEEP'
    return 'NO CLEAR SWEEP'

def fvg_state(d):
    if len(d)<5:return ('NONE',0)
    x=d.tail(120).reset_index(drop=True);bull=bear=0
    for i in range(2,len(x)):
        bull += int(x.Low.iloc[i]>x.High.iloc[i-2]); bear += int(x.High.iloc[i]<x.Low.iloc[i-2])
    return ('BULL FVG' if bull>bear else 'BEAR FVG' if bear>bull else 'MIXED FVG',bull+bear)

def ob_state(d):
    if len(d)<10:return 'NO DATA'
    x=enrich(d);last=x.iloc[-1];rng=max(float(last.High-last.Low),1e-9);body=abs(float(last.Close-last.Open));vol=float(last.VOLR) if pd.notna(last.VOLR) else 1
    if body/rng>.65 and vol>1.2:return 'DISPLACEMENT / FRESH ZONE'
    return 'POTENTIAL OB — VERIFY CANDLE BASE'

def amd_state(d):
    if len(d)<30:return 'INSUFFICIENT DATA'
    x=d.tail(30);rng=float(x.High.max()-x.Low.min());atr=float(enrich(d).ATR.iloc[-1]) if pd.notna(enrich(d).ATR.iloc[-1]) else rng/10;recent=x.tail(5);compression=float(recent.High.max()-recent.Low.min())/max(rng,1e-9);sweep=liquidity(d);last=x.iloc[-1];disp=abs(float(last.Close-last.Open))/max(atr,1e-9)
    if compression<.35 and ('SWEEP' in sweep or disp>1.5):return 'MANIPULATION → DISPLACEMENT'
    if compression<.35:return 'ACCUMULATION / COMPRESSION'
    if disp>1.5:return 'DISTRIBUTION / EXPANSION'
    return 'NO CLEAR AMD PHASE'

def mtf_fetch(sym):
    specs={'1W':('5y','1wk'),'1D':('2y','1d'),'1H':('730d','1h'),'30M':('60d','30m'),'15M':('60d','15m'),'5M':('60d','5m'),'1M':('7d','1m')}
    out={k:fetch(sym,*v) for k,v in specs.items()}
    if not out['1H'].empty:
        x=out['1H'].copy();
        try:
            o=x['Open'].resample('4h').first();h=x['High'].resample('4h').max();l=x['Low'].resample('4h').min();c=x['Close'].resample('4h').last();v=x['Volume'].resample('4h').sum();out['4H']=pd.concat([o,h,l,c,v],axis=1).dropna()
        except Exception:out['4H']=pd.DataFrame()
    else:out['4H']=pd.DataFrame()
    return out

def mtf_analysis(sym):
    data=mtf_fetch(sym);rows=[];score=0
    for tf in MTFS:
        d=data.get(tf,pd.DataFrame());s=structure(d);f,n=fvg_state(d);liq=liquidity(d) if not d.empty else 'NO DATA';score += WEIGHTS[tf]*(s['score']/5 if s['score'] else 0)
        rows.append([tf,s['bias'],s['score'],round(s.get('rsi',0),1) if s.get('rsi') else '—',liq,f])
    return data,pd.DataFrame(rows,columns=['TF','STRUCTURE','SCORE','RSI','LIQUIDITY','FVG']),round(score,1)

def core_signal(data):
    h4=structure(data.get('4H',pd.DataFrame()));h1=structure(data.get('1H',pd.DataFrame()));m15=structure(data.get('15M',pd.DataFrame()));m5=structure(data.get('5M',pd.DataFrame()));loc=1 if h4['bias']!='NO DATA' and (h4['score']>=3 or h4['score']<=2) else 0;liq=(1 if 'SWEEP' in liquidity(data.get('1H',pd.DataFrame())) else 0);trig=1 if (m5['score']>=4 and m15['score']>=3) or (m5['score']<=1 and m15['score']<=2) else 0
    direction='BUY' if h4['score']>=3 and h1['score']>=3 else 'SELL' if h4['score']<=2 and h1['score']<=2 else 'WAIT';score=int(min(99,45+loc*15+liq*10+trig*15+max(h4['score'],5-h4['score'])*3));status='VALID CORE CANDIDATE' if score>=75 and direction!='WAIT' else 'WAIT — NEED LOCATION/TRIGGER'
    return direction,score,status

def early_signal(data):
    d=data.get('1H',pd.DataFrame());amd=amd_state(d);liq=liquidity(d);f,n=fvg_state(d);score=45+(15 if 'SWEEP' in liq else 0)+(15 if 'COMPRESSION' in amd or 'MANIPULATION' in amd else 0)+(10 if n else 0);return min(90,score),amd,liq,f

def scan_rows(symbols,kind='Core'):
    syms=list(dict.fromkeys(symbols));batch=fetch_batch(syms,'6mo','1d');rows=[]
    for sym,d in batch.items():
        if d.empty:continue
        s=structure(d);liq=liquidity(d);f,n=fvg_state(d);direction='BUY' if s['score']>=4 else 'SELL' if s['score']<=1 else 'WAIT';score=min(99,55+s['score']*7+(10 if 'SWEEP' in liq else 0)+(5 if n else 0));rows.append([sym,direction,round(s['rsi'],1),liq,f,score])
    return pd.DataFrame(rows,columns=['SYMBOL','DIRECTION','RSI','LIQUIDITY','FVG','SCORE']).sort_values('SCORE',ascending=False) if rows else pd.DataFrame(columns=['SYMBOL','DIRECTION','RSI','LIQUIDITY','FVG','SCORE'])

def chart(d,height=330):
    if go is None or d.empty:return None
    x=enrich(d).tail(180);fig=go.Figure();fig.add_trace(go.Candlestick(x=x.index,open=x.Open,high=x.High,low=x.Low,close=x.Close,name='Price',increasing_line_color='#6fcf97',decreasing_line_color='#d77a7a'))
    for col,name,colr in [('EMA18','EMA18','#ffd34e'),('EMA50','EMA50','#13d8ff')]:fig.add_trace(go.Scatter(x=x.index,y=x[col],name=name,line=dict(color=colr,width=1.4)))
    fig.update_layout(height=height,margin=dict(l=5,r=5,t=20,b=5),paper_bgcolor='#06111d',plot_bgcolor='#06111d',font_color='#dce8ef',xaxis_rangeslider_visible=False,legend=dict(orientation='h'))
    return fig

def ai_analyze(images,symbol,model):
    key=os.getenv('OPENAI_API_KEY','')
    try:key=key or st.secrets.get('OPENAI_API_KEY','')
    except Exception:pass
    if not key:return 'OPENAI_API_KEY is not configured. Add it in Streamlit App Settings → Secrets.'
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key);content=[{'type':'input_text','text':f'''You are VS FLOW AI. Symbol: {symbol or 'unknown'}. Analyze the supplied chart screenshots using 1W→1D→4H→1H→30M→15M→5M→1M. Core rule: LOCATION→LIQUIDITY→TRIGGER→ENTRY. Higher timeframe decides WHERE; lower timeframe decides WHEN. Evaluate supply/demand, premium/discount, OB, FVG/iFVG, AMD, liquidity sweep, BOS/CHoCH, trendline, 18-day MA, volume, volatility, correction quality and risk. Return a strict VFTC with: Analysis Overview; Bias; Confidence; Entry Zone; SL; TP1/TP2/TP3; R:R; Market Context; MTF table; Core Setup; Early Setup; AMD+iFVG; Invalidation; Final Result. Use only visible evidence; do not invent unreadable prices or guarantee outcomes.'''}]
        for b in images:content.append({'type':'input_image','image_url':f"data:{b['mime']};base64,{base64.b64encode(b['bytes']).decode()}"})
        r=client.responses.create(model=model,input=[{'role':'user','content':content}],max_output_tokens=6000);return r.output_text
    except Exception as e:return f'AI analysis error: {e}'


def world_class_analysis(data):
    h4=structure(data.get('4H',pd.DataFrame())); h1=structure(data.get('1H',pd.DataFrame())); d1=structure(data.get('1D',pd.DataFrame()))
    d4=data.get('4H',pd.DataFrame()); d1h=data.get('1H',pd.DataFrame())
    e18=eighteen_day_ma(d4); liq=liquidity(d1h); fvg,n=fvg_state(d1h); amd=amd_state(d1h)
    trend=round(((d1.get('score',0)/5)*100 + (h4.get('score',0)/5)*100)/2,1) if d1.get('score') is not None else 0
    correction=70 if ('MIXED' in h1.get('bias','') or h1.get('score',0) in [2,3]) else 45
    liquidity_score=90 if 'SWEEP' in liq else 55
    breakout=85 if h1.get('score',0) in [1,4,5] else 50
    quant=backtest_quality(d4)
    return pd.DataFrame([
        ['Pau-style trend → correction → key level', correction, 'Correction quality + key-level context'],
        ['Inna 18-day MA', e18['score'], e18['state']],
        ['PTJ risk / asymmetric R:R', min(95, round((trend+liquidity_score)/2,1)), 'Capital preservation gate'],
        ['Richard Dennis breakout', breakout, 'Structure / breakout pressure'],
        ['Jim Simons quant validation', quant, 'Historical rule stability proxy'],
        ['Darvas box / compression', 75 if 'COMPRESSION' in amd else 45, amd],
        ['Livermore trend / winner management', trend, d1.get('bias','NO DATA')],
        ['Suricate COT / term structure / volume', volume_context(d4), 'Volume/volatility context proxy'],
    ],columns=['FRAMEWORK','SCORE','INTEGRATION'])

def backtest_quality(d):
    if d is None or d.empty or len(d)<80:return 50
    x=enrich(d).dropna(subset=['EMA18']).copy(); sig=x.Close>x.EMA18; fwd=x.Close.pct_change().shift(-1); r=fwd.where(sig,-fwd).dropna()
    if r.empty:return 50
    hit=float((r>0).mean())*100; avg=float(r.mean())*100; dd=float(((1+r).cumprod()/(1+r).cumprod().cummax()-1).min()*100)
    return int(np.clip(50+0.35*(hit-50)+4*avg+0.15*dd,0,100))

def volume_context(d):
    if d is None or d.empty:return 50
    x=enrich(d); v=float(x.VOLR.iloc[-1]) if pd.notna(x.VOLR.iloc[-1]) else 1
    return int(np.clip(50+(v-1)*35,0,100))

def eighteen_day_ma(d):
    if d is None or d.empty or len(d)<20:return {'state':'NO DATA','score':0,'ma':None}
    x=d.copy(); x['MA18']=x.Close.rolling(18).mean(); last=x.iloc[-1]; ma=float(last.MA18); close=float(last.Close)
    slope=float(x.MA18.iloc[-1]-x.MA18.iloc[-6]) if len(x)>=24 else 0
    state='ABOVE + RISING' if close>ma and slope>0 else 'BELOW + FALLING' if close<ma and slope<0 else 'MIXED'
    score=90 if state=='ABOVE + RISING' else 90 if state=='BELOW + FALLING' else 55
    return {'state':state,'score':score,'ma':ma}

def ifvg_state(d):
    if d is None or len(d)<6:return 'NO DATA'
    x=d.tail(80).reset_index(drop=True)
    bull=bear=0
    for i in range(2,len(x)):
        bull += int(x.Low.iloc[i] > x.High.iloc[i-2])
        bear += int(x.High.iloc[i] < x.Low.iloc[i-2])
    # inverse proxy: an old imbalance that has been crossed/closed through
    close=float(x.Close.iloc[-1]); hi=float(x.High.tail(8).max()); lo=float(x.Low.tail(8).min())
    if bull>bear and close<lo*1.002:return 'BULL FVG → INVERSE / FAILED'
    if bear>bull and close>hi*0.998:return 'BEAR FVG → INVERSE / FAILED'
    return 'BULL iFVG CONTEXT' if bull>bear else 'BEAR iFVG CONTEXT' if bear>bull else 'NO CLEAR iFVG'

def excel_bytes(df, sheets=None):
    if Workbook is None:return None
    sheets=sheets or {'Scanner':df}
    wb=Workbook(); first=True
    for name,frame in sheets.items():
        ws=wb.active if first else wb.create_sheet(); first=False; ws.title=str(name)[:31]
        f=frame.copy() if isinstance(frame,pd.DataFrame) else pd.DataFrame(frame)
        for j,col in enumerate(f.columns,1):
            c=ws.cell(1,j,col); c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='0B2940'); c.alignment=Alignment(horizontal='center')
        for row in f.itertuples(index=False):ws.append(list(row))
        ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
        for col in ws.columns:
            letter=col[0].column_letter; ws.column_dimensions[letter].width=min(max(12,max(len(str(x.value or '')) for x in col)+2),36)
    bio=io.BytesIO();wb.save(bio);return bio.getvalue()

def pdf_bytes(title,df,subtitle='VS FLOW AI MASTER • Educational / research use only'):
    if SimpleDocTemplate is None:return None
    bio=io.BytesIO();doc=SimpleDocTemplate(bio,pagesize=landscape(A4),leftMargin=20,rightMargin=20,topMargin=20,bottomMargin=20)
    styles=getSampleStyleSheet();story=[Paragraph(title,styles['Title']),Paragraph(subtitle,styles['Normal']),Spacer(1,10)]
    f=df.copy();
    for c in f.columns:f[c]=f[c].astype(str).str.slice(0,28)
    data=[list(f.columns)]+f.head(70).values.tolist()
    t=Table(data,repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B2940')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#9AA8B2')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t);doc.build(story);return bio.getvalue()

def nse_options(symbol='NIFTY', expiry=None):
    if requests is None:return None,'requests unavailable'
    symbol=str(symbol).upper().strip(); indices={'NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY','NIFTYNXT50'}
    try:
        s=requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36','Accept':'application/json,text/plain,*/*','Accept-Language':'en-US,en;q=0.9','Referer':'https://www.nseindia.com/option-chain','Connection':'keep-alive'})
        home=s.get('https://www.nseindia.com',timeout=12); home.raise_for_status()
        info_url='https://www.nseindia.com/api/option-chain-contract-info'
        ir=s.get(info_url,params={'symbol':symbol},timeout=12)
        ir.raise_for_status(); info=ir.json()
        expiries=info.get('expiryDates') or info.get('records',{}).get('expiryDates') or info.get('data',{}).get('expiryDates') or []
        if not expiries:
            # fallback to legacy contract info shape
            expiries=info.get('records',{}).get('expiryDates',[])
        exp=expiry or (expiries[0] if expiries else None)
        if not exp:raise RuntimeError('NSE did not return an expiry date. Try again or use the NSE CSV/JSON import below.')
        typ='Indices' if symbol in indices else 'Equity'
        url='https://www.nseindia.com/api/option-chain-v3'
        r=s.get(url,params={'type':typ,'symbol':symbol,'expiry':exp},timeout=15)
        if r.status_code in (401,403,404):
            # retry with fresh session and browser-like headers
            s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/154 Safari/537.36','Accept':'application/json, text/plain, */*','Referer':'https://www.nseindia.com/option-chain?symbol='+symbol})
            s.get('https://www.nseindia.com',timeout=12);r=s.get(url,params={'type':typ,'symbol':symbol,'expiry':exp},timeout=15)
        r.raise_for_status();j=r.json();records=j.get('records',{}); rows=records.get('data',[]) or j.get('data',[]) or []
        spot=records.get('underlyingValue') or j.get('underlyingValue')
        out=[]
        for z in rows:
            ce=z.get('CE') or {}; pe=z.get('PE') or {}
            out.append({'expiry':z.get('expiryDate',exp),'strike':z.get('strikePrice'),'CE_OI':ce.get('openInterest',0),'CE_ChgOI':ce.get('changeinOpenInterest',0),'CE_Vol':ce.get('totalTradedVolume',0),'CE_IV':ce.get('impliedVolatility'),'CE_LTP':ce.get('lastPrice'),'CE_Bid':ce.get('bidprice'),'CE_Ask':ce.get('askPrice'),'PE_Bid':pe.get('bidprice'),'PE_Ask':pe.get('askPrice'),'PE_LTP':pe.get('lastPrice'),'PE_IV':pe.get('impliedVolatility'),'PE_Vol':pe.get('totalTradedVolume',0),'PE_ChgOI':pe.get('changeinOpenInterest',0),'PE_OI':pe.get('openInterest',0)})
        df=pd.DataFrame(out).dropna(subset=['strike'])
        return {'spot':spot,'expiry':exp,'expiries':expiries,'df':df},None
    except Exception as e:return None,str(e)

def parse_option_upload(upload):
    if upload is None:return None,None
    try:
        raw=upload.getvalue(); name=upload.name.lower()
        if name.endswith('.csv'):
            df=pd.read_csv(io.BytesIO(raw)); return {'spot':None,'expiry':None,'df':normalize_option_df(df)},None
        j=json.loads(raw.decode('utf-8')); rows=j.get('records',{}).get('data',[]) or j.get('data',[])
        out=[]
        for z in rows:
            ce=z.get('CE') or {};pe=z.get('PE') or {};out.append({'expiry':z.get('expiryDate'),'strike':z.get('strikePrice'),'CE_OI':ce.get('openInterest',0),'CE_IV':ce.get('impliedVolatility'),'CE_LTP':ce.get('lastPrice'),'PE_OI':pe.get('openInterest',0),'PE_IV':pe.get('impliedVolatility'),'PE_LTP':pe.get('lastPrice')})
        return {'spot':j.get('records',{}).get('underlyingValue'),'expiry':j.get('records',{}).get('expiryDates',[None])[0] if j.get('records',{}).get('expiryDates') else None,'df':pd.DataFrame(out)},None
    except Exception as e:return None,str(e)

def normalize_option_df(df):
    x=df.copy(); x.columns=[str(c).strip() for c in x.columns]
    aliases={'strikePrice':'strike','Strike Price':'strike','Strike':'strike','CALLS - OI':'CE_OI','PUTS - OI':'PE_OI','CE OI':'CE_OI','PE OI':'PE_OI'}
    x=x.rename(columns=aliases)
    for c in ['strike','CE_OI','PE_OI','CE_IV','PE_IV','CE_LTP','PE_LTP']:
        if c not in x:x[c]=np.nan
    return x

def max_pain(df):
    if df is None or df.empty:return None
    strikes=df['strike'].astype(float).values;best=None
    for s in strikes:
        call=((s-strikes).clip(min=0)*df.CE_OI.fillna(0)).sum();put=((strikes-s).clip(min=0)*df.PE_OI.fillna(0)).sum();pain=call+put
        if best is None or pain<best[1]:best=(s,pain)
    return best[0] if best else None


def card_html(name, sym, market=''):
    d=fetch(sym,'5d','1d')
    if d.empty:
        return f'<div class="ticker"><div class="name">{name}</div><div class="px">—</div><div class="small">Data unavailable</div></div>'
    last=float(d.Close.iloc[-1]); prev=float(d.Close.iloc[-2]) if len(d)>1 else last; chg=(last/prev-1)*100 if prev else 0
    return f'<div class="ticker"><div class="name">{name}</div><div class="px">{last:,.2f}</div><div class="{"up" if chg>=0 else "down"}">{"▲" if chg>=0 else "▼"} {chg:+.2f}%</div><div class="small">{market}</div></div>'

def render_universe_cards(items, cols=4):
    for i in range(0,len(items),cols):
        cs=st.columns(cols)
        for c,(name,sym) in zip(cs,items[i:i+cols]): c.markdown(card_html(name,sym),unsafe_allow_html=True)

def render_market_dashboard(title, subtitle, benchmarks, universe_label, universe_symbols, color='cyan'):
    st.markdown(f'<div class="section-title">{title} <span class="small">{subtitle}</span></div>',unsafe_allow_html=True)
    # benchmark cards
    render_universe_cards(benchmarks, cols=4)
    st.markdown(f'<div class="panel" style="margin-top:10px"><b class="{color}">{universe_label}</b><br><span class="small">{len(universe_symbols)} instruments available • click Universal Search or Master Scanner for full MTF analysis</span></div>',unsafe_allow_html=True)
    # regime / breadth / universe
    c1,c2,c3=st.columns([1,2,1])
    with c1:
        base=benchmarks[0][1] if benchmarks else '^NSEI'; d=fetch(base,'6mo','1d'); ss=structure(d); cls='green' if 'BULL' in ss['bias'] else 'red' if 'BEAR' in ss['bias'] else 'gold'
        st.markdown(f'<div class="panel"><div class="small">MARKET REGIME</div><div class="regime-big {cls}">{ss["bias"]}</div><div class="bullet">EMA18 / EMA50 / EMA200</div><div class="bullet">RSI {ss.get("rsi",0):.1f}</div></div>',unsafe_allow_html=True)
    with c2:
        rows=[]
        for n,sym in benchmarks[:8]:
            d=fetch(sym,'6mo','1d'); ss=structure(d); rows.append([n,ss['bias'],ss.get('score',0),round(ss.get('rsi',0),1) if ss.get('rsi') else '—'])
        st.dataframe(pd.DataFrame(rows,columns=['ASSET','REGIME','SCORE','RSI']),use_container_width=True,hide_index=True)
    with c3:
        st.metric('UNIVERSE',len(universe_symbols));st.metric('MTF', '1W → 1M');st.caption('Final trade requires manual MTF confirmation.')
    st.markdown('### TODAY\'S SETUP RADAR')
    sample=universe_symbols[:20]
    if st.button(f'🚀 RUN {universe_label.upper()} RADAR',key='radar_'+title.replace(' ','_'),use_container_width=True):
        with st.spinner(f'Scanning {len(sample)} candidates…'): st.session_state['radar_'+title]=scan_rows(sample)
    if 'radar_'+title in st.session_state:
        df=st.session_state['radar_'+title];st.dataframe(df,use_container_width=True,hide_index=True,height=420)
        x=excel_bytes(df,{'Radar':df});p=pdf_bytes(f'{title} Radar',df);a,b=st.columns(2)
        if x:a.download_button('⬇️ EXCEL',x,file_name=re.sub(r'[^A-Za-z0-9]+','_',title)+'_Radar.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key='ex_'+title,use_container_width=True)
        if p:b.download_button('⬇️ PDF',p,file_name=re.sub(r'[^A-Za-z0-9]+','_',title)+'_Radar.pdf',mime='application/pdf',key='pdf_'+title,use_container_width=True)
    st.markdown('### ASSET UNIVERSE')
    tabs=st.tabs(['Top / Major','All Symbols'])
    with tabs[0]:
        render_universe_cards([(x,x) for x in universe_symbols[:min(24,len(universe_symbols))]],cols=4)
    with tabs[1]:
        st.dataframe(pd.DataFrame({'SYMBOL':universe_symbols}),use_container_width=True,hide_index=True,height=420)
        x=excel_bytes(pd.DataFrame({'SYMBOL':universe_symbols}),{'Universe':pd.DataFrame({'SYMBOL':universe_symbols})});p=pdf_bytes(f'{title} Universe',pd.DataFrame({'SYMBOL':universe_symbols}));a,b=st.columns(2)
        if x:a.download_button('⬇️ DOWNLOAD UNIVERSE • EXCEL',x,file_name=re.sub(r'[^A-Za-z0-9]+','_',title)+'_Universe.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key='ux_'+title,use_container_width=True)
        if p:b.download_button('⬇️ DOWNLOAD UNIVERSE • PDF',p,file_name=re.sub(r'[^A-Za-z0-9]+','_',title)+'_Universe.pdf',mime='application/pdf',key='up_'+title,use_container_width=True)

def render_world_class_page():
    st.markdown('<div class="section-title">🏆 WORLD-CLASS STRATEGY LAB • PAU • INNA • PTJ • DENNIS • SIMONS • DARVAS • LIVERMORE • SURICATE</div>',unsafe_allow_html=True)
    sym=resolve(st.text_input('Symbol / instrument','NIFTY',key='wcl_v7_sym'),'Auto')
    frameworks=[('Pau Perdices Bellet','Trend → correction → key level → reversal + risk'),('Inna Rosputnia','18-day MA trend following + systematic discipline'),('Paul Tudor Jones','Capital preservation + asymmetric R:R'),('Richard Dennis','Breakout + ATR risk'),('Jim Simons','Quant validation / systematic testing'),('Darvas','Box breakout + compression'),('Livermore','Trend + winner management'),('Suricate Trading','COT + term structure + volume profile')]
    st.dataframe(pd.DataFrame(frameworks,columns=['FRAMEWORK','INTEGRATION']),use_container_width=True,hide_index=True)
    if st.button('🏆 RUN SYMBOL-SPECIFIC WORLD-CLASS ANALYSIS',type='primary',use_container_width=True):
        with st.spinner('Running MTF + world-class confluence…'):
            data=mtf_fetch(sym); w=world_class_analysis(data); st.session_state.wcl_v7=(sym,w,data)
    if 'wcl_v7' in st.session_state:
        sym,w,data=st.session_state.wcl_v7
        c=st.columns(5); c[0].metric('SYMBOL',sym); c[1].metric('CONFLUENCE',f'{float(w.SCORE.mean()):.1f}/100'); c[2].metric('18-DAY MA',eighteen_day_ma(data.get('1D',pd.DataFrame()))['state']); c[3].metric('LIQUIDITY',liquidity(data.get('1H',pd.DataFrame()))); c[4].metric('AMD',amd_state(data.get('1H',pd.DataFrame())))
        st.dataframe(w,use_container_width=True,hide_index=True)
        x=excel_bytes(w,{'World Class':w});p=pdf_bytes(f'VS FLOW World-Class — {sym}',w);a,b=st.columns(2)
        if x:a.download_button('⬇️ WORLD-CLASS • EXCEL',x,file_name=f'VS_FLOW_WorldClass_{re.sub(r"[^A-Za-z0-9_-]","_",sym)}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        if p:b.download_button('⬇️ WORLD-CLASS • PDF',p,file_name=f'VS_FLOW_WorldClass_{re.sub(r"[^A-Za-z0-9_-]","_",sym)}.pdf',mime='application/pdf',use_container_width=True)


def market_snapshot_rows(symbols):
    rows=[]
    batch=fetch_batch(list(dict.fromkeys(symbols)),'3mo','1d')
    for sym,d in batch.items():
        if d.empty: continue
        z=structure(d); e=eighteen_day_ma(d); liq=liquidity(d); f,n=fvg_state(d)
        last=float(z.get('close',0) or 0); prev=float(d.Close.iloc[-2]) if len(d)>1 else last
        chg=(last/prev-1)*100 if prev else 0
        rows.append([sym,last,chg,z.get('bias','NO DATA'),z.get('rsi','—'),int(z.get('score',0)*20),e['state'],liq,f])
    return pd.DataFrame(rows,columns=['SYMBOL','LTP','DAY %','REGIME','RSI','VS FLOW SCORE','18D MA','LIQUIDITY','FVG']).sort_values('VS FLOW SCORE',ascending=False) if rows else pd.DataFrame(columns=['SYMBOL','LTP','DAY %','REGIME','RSI','VS FLOW SCORE','18D MA','LIQUIDITY','FVG'])

def pattern_scan(d):
    if d is None or d.empty or len(d)<30:
        return {'patterns':[],'regime':'INSUFFICIENT DATA','score':0}
    x=enrich(d).copy(); last=x.iloc[-1]; prev=x.iloc[-2]; patterns=[]
    body=abs(float(last.Close-last.Open)); rng=max(float(last.High-last.Low),1e-9)
    prev_body=abs(float(prev.Close-prev.Open));
    if float(last.High)>float(x.High.iloc[-21:-1].max()) and float(last.Close)>float(x.High.iloc[-21:-1].max()): patterns.append('20D BREAKOUT')
    if float(last.Low)<float(x.Low.iloc[-21:-1].min()) and float(last.Close)<float(x.Low.iloc[-21:-1].min()): patterns.append('20D BREAKDOWN')
    if float(last.High)<float(prev.High) and float(last.Low)>float(prev.Low): patterns.append('INSIDE BAR')
    if float(last.Close)>float(last.Open) and float(prev.Close)<float(prev.Open) and float(last.Close)>float(prev.Open) and float(last.Open)<float(prev.Close): patterns.append('BULLISH ENGULFING')
    if float(last.Close)<float(last.Open) and float(prev.Close)>float(prev.Open) and float(last.Close)<float(prev.Open) and float(last.Open)>float(prev.Close): patterns.append('BEARISH ENGULFING')
    if body/rng<0.25: patterns.append('LOW-BODY / INDECISION')
    if len(x)>=10:
        recent=float(x.High.tail(10).max()-x.Low.tail(10).min()); broad=float(x.High.tail(40).max()-x.Low.tail(40).min())
        if broad and recent/broad<0.35: patterns.append('COMPRESSION')
    if pd.notna(last.VOLR) and float(last.VOLR)>1.8: patterns.append('VOLUME EXPANSION')
    regime=structure(d)['bias']; score=min(100,40+len(patterns)*10+(15 if 'TREND' in regime else 0)+(10 if 'BREAKOUT' in ' '.join(patterns) else 0))
    return {'patterns':patterns,'regime':regime,'score':score}

def render_super_computer():
    st.markdown('''<div class="super-hero"><h1>VS FLOW SUPER COMPUTER</h1><p>GLOBAL MARKET INTELLIGENCE • MULTI-ASSET RESEARCH • MTF EXECUTION ENGINE • ONE TERMINAL</p><div class="gold-rule"></div></div>''',unsafe_allow_html=True)
    st.caption('Live data is provider-dependent. Scanner candidates never replace the full VS FLOW MTF confirmation rule.')
    # Core command metrics
    universe_count=len(set([x+'.NS' for x in INDIA100]+GLOBAL_STOCKS+GLOBAL_INDICES+CRYPTO+COMMODITIES))
    watch=st.session_state.get('watchlist', ['^NSEI','^NSEBANK','^GSPC','^IXIC','BTC-USD','GC=F','CL=F','EURUSD=X'])
    snap=market_snapshot_rows(watch)
    bull=int((snap.REGIME.str.contains('BULL',na=False)).sum()) if not snap.empty else 0
    bear=int((snap.REGIME.str.contains('BEAR',na=False)).sum()) if not snap.empty else 0
    avg=int(snap['VS FLOW SCORE'].mean()) if not snap.empty else 0
    st.markdown(f'''<div class="command-grid"><div class="command-card"><div class="label">MARKET UNIVERSE</div><div class="value">{universe_count:,}+</div><div class="subv">curated instruments + custom import</div></div><div class="command-card"><div class="label">WATCHLIST BREADTH</div><div class="value">{bull} BULL / {bear} BEAR</div><div class="subv">current provider snapshot</div></div><div class="command-card"><div class="label">VS FLOW SCORE</div><div class="value">{avg}/100</div><div class="subv">watchlist composite</div></div><div class="command-card"><div class="label">ENGINE</div><div class="value">8-TF</div><div class="subv">1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M</div></div></div>''',unsafe_allow_html=True)
    st.markdown('### 🌐 GLOBAL MARKET PULSE')
    pulse=[('🇮🇳 NIFTY','^NSEI'),('🇮🇳 BANK','^NSEBANK'),('🇺🇸 S&P 500','^GSPC'),('🇺🇸 NASDAQ','^IXIC'),('🇯🇵 NIKKEI','^N225'),('🇩🇪 DAX','^GDAXI'),('🇬🇧 FTSE','^FTSE'),('🇭🇰 HSI','^HSI'),('₿ BTC','BTC-USD'),('🥇 GOLD','GC=F'),('🛢️ WTI','CL=F'),('💱 EURUSD','EURUSD=X')]
    render_universe_cards(pulse,cols=4)
    left,right=st.columns([1.55,1])
    with left:
        st.markdown('### 🧠 MARKET INTELLIGENCE GRID')
        st.dataframe(snap,use_container_width=True,hide_index=True,height=370)
        if not snap.empty:
            x=excel_bytes(snap,{'Market Pulse':snap});
            if x: st.download_button('⬇️ EXPORT MARKET PULSE',x,'VS_FLOW_Market_Pulse.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
    with right:
        st.markdown('### 🎯 DECISION GATE')
        st.markdown('<div class="panel"><b>VS FLOW RULE</b><br><br>1. Establish HTF location<br>2. Identify liquidity<br>3. Wait for lower-TF trigger<br>4. Confirm entry + invalidation<br>5. Calculate R:R<br>6. Execute only if rules align<br><br><span class="gold">WAIT is a valid result.</span></div>',unsafe_allow_html=True)
        st.markdown('### ⚡ QUICK COMMANDS')
        if st.button('🔥 RUN INDIA CORE RADAR',use_container_width=True):
            st.session_state.quick_scan=scan_rows([x+'.NS' for x in INDIA100[:35]])
        if st.button('🌎 RUN GLOBAL RADAR',use_container_width=True):
            st.session_state.quick_scan=scan_rows(GLOBAL_STOCKS[:40]+CRYPTO[:10]+COMMODITIES[:8])
    if 'quick_scan' in st.session_state:
        st.markdown('### 🔎 LATEST SCAN RESULT')
        st.dataframe(st.session_state.quick_scan,use_container_width=True,hide_index=True,height=300)
    st.markdown('### 🗺️ ASSET CONTROL ROOM')
    a,b,c,d,e=st.columns(5)
    a.metric('INDIA',len(INDIA100),'stocks')
    b.metric('GLOBAL EQUITIES',len(GLOBAL_STOCKS),'curated')
    c.metric('INDICES',len(GLOBAL_INDICES),'global')
    d.metric('CRYPTO',len(CRYPTO),'major')
    e.metric('COMMODITIES',len(COMMODITIES),'futures')
    st.info('For broader global coverage, use Asset Universe → Custom Import to load an exchange/vendor symbol list. The engine does not fabricate missing securities or prices.')

def render_pattern_lab():
    st.markdown('<div class="super-hero"><h1>VS PATTERN LAB</h1><p>MULTI-TIMEFRAME PATTERN RESEARCH • BREAKOUT • COMPRESSION • CANDLE STRUCTURE • HISTORICAL CONTEXT</p><div class="gold-rule"></div></div>',unsafe_allow_html=True)
    col1,col2=st.columns([2,1]);
    with col1: q=st.text_input('Research instrument','NIFTY',key='pattern_sym')
    with col2: tf=st.selectbox('Research timeframe',['1D','4H','1H','15M','5M'],key='pattern_tf')
    sym=resolve(q,'Auto'); period={'1D':'2y','4H':'730d','1H':'730d','15M':'60d','5M':'60d'}[tf]; interval={'1D':'1d','4H':'1h','1H':'1h','15M':'15m','5M':'5m'}[tf]
    d=fetch(sym,period,interval)
    if d.empty: st.warning('No data available for this instrument/timeframe.');
    else:
        if tf=='4H':
            try:
                d=pd.concat([d.Open.resample('4h').first(),d.High.resample('4h').max(),d.Low.resample('4h').min(),d.Close.resample('4h').last(),d.Volume.resample('4h').sum()],axis=1).dropna();d.columns=['Open','High','Low','Close','Volume']
            except Exception: pass
        res=pattern_scan(d);c=st.columns(4);c[0].metric('REGIME',res['regime']);c[1].metric('PATTERN EVENTS',len(res['patterns']));c[2].metric('RESEARCH SCORE',f"{res['score']}/100");c[3].metric('LTP',f"{float(d.Close.iloc[-1]):,.2f}")
        st.markdown('### DETECTED STRUCTURES')
        st.dataframe(pd.DataFrame({'PATTERN':res['patterns']}) if res['patterns'] else pd.DataFrame({'PATTERN':['No high-confidence pattern detected']}),use_container_width=True,hide_index=True)
        fig=chart(d,480)
        if fig: st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('### MTF RESEARCH')
        data,mtf,score=mtf_analysis(sym);st.dataframe(mtf,use_container_width=True,hide_index=True);st.caption(f'VS FLOW MTF composite: {score}/100. Pattern detection is research-only; final execution requires location + liquidity + trigger.')

def render_watchlist_alerts():
    st.markdown('<div class="super-hero"><h1>WATCHLIST & ALERT ENGINE</h1><p>PERSONAL MARKET RADAR • PRICE • TREND • LIQUIDITY • VS FLOW SCORE</p><div class="gold-rule"></div></div>',unsafe_allow_html=True)
    default='NIFTY, BANKNIFTY, S&P500, NASDAQ, BTC, GOLD, CRUDE, AAPL, NVDA, RELIANCE'
    raw=st.text_area('Watchlist symbols',', '.join(st.session_state.get('watchlist_names',default.split(', '))),height=80)
    names=[x.strip() for x in re.split(r'[,\n;]+',raw) if x.strip()]; syms=[resolve(x,'Auto') for x in names]
    if st.button('💾 UPDATE WATCHLIST',type='primary'): st.session_state.watchlist=syms;st.session_state.watchlist_names=names
    snap=market_snapshot_rows(syms);st.dataframe(snap,use_container_width=True,hide_index=True,height=450)
    st.markdown('### 🔔 CONDITION MONITOR')
    threshold=st.slider('Alert when VS FLOW score is at least',50,95,75)
    if not snap.empty:
        hits=snap[snap['VS FLOW SCORE']>=threshold]
        if hits.empty: st.info('No instruments currently meet the selected threshold.')
        else:
            for _,r in hits.iterrows(): st.markdown(f'<div class="watch-card"><span class="status-dot"></span><b>{r.SYMBOL}</b> • Score <b>{int(r["VS FLOW SCORE"])}/100</b> • {r.REGIME} • Liquidity: {r.LIQUIDITY}</div>',unsafe_allow_html=True)
    st.caption('This is a dashboard condition monitor, not an automatic broker execution system.')

def render_risk_command():
    st.markdown('<div class="super-hero"><h1>RISK COMMAND CENTER</h1><p>POSITION SIZE • MAX LOSS • R:R • PORTFOLIO EXPOSURE • VFTC RISK GATE</p><div class="gold-rule"></div></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3);capital=a.number_input('Account capital',value=20000.0,min_value=0.0,step=1000.0);risk_pct=b.number_input('Risk per trade %',value=1.0,min_value=0.0,max_value=10.0,step=.25);entry=c.number_input('Entry price',value=100.0,min_value=0.0)
    d,e,f=st.columns(3);sl=d.number_input('Stop Loss',value=95.0,min_value=0.0);tp=e.number_input('Target',value=110.0,min_value=0.0);lot=f.number_input('Lot / unit multiplier',value=1.0,min_value=.0001,step=1.0)
    risk_amt=capital*risk_pct/100;unit_risk=abs(entry-sl);qty=(risk_amt/unit_risk) if unit_risk else 0;reward=abs(tp-entry);rr=(reward/unit_risk) if unit_risk else 0
    x,y,z,w=st.columns(4);x.metric('MAX LOSS',f'₹{risk_amt:,.2f}');y.metric('POSITION UNITS',f'{qty:,.2f}');z.metric('R:R',f'1:{rr:.2f}');w.metric('RISK GATE','PASS' if rr>=2 else 'REVIEW')
    st.markdown('<div class="panel"><b>VS FLOW RISK RULES</b><br>• Define invalidation before entry<br>• Size from risk, not conviction<br>• Avoid averaging into invalidation<br>• Respect daily loss limit<br>• A setup without acceptable R:R is not an execution setup</div>',unsafe_allow_html=True)


# persistent session state defaults
if 'watchlist' not in st.session_state:
    st.session_state.watchlist=['^NSEI','^NSEBANK','^GSPC','^IXIC','BTC-USD','GC=F','CL=F','EURUSD=X']
if 'watchlist_names' not in st.session_state:
    st.session_state.watchlist_names=['NIFTY','BANKNIFTY','S&P500','NASDAQ','BTC','GOLD','CRUDE','EURUSD']
if 'journal' not in st.session_state:
    st.session_state.journal=[]

# sidebar
with st.sidebar:
    if LOGO.exists():st.image(str(LOGO),use_container_width=True)
    st.markdown('### 🧠 VS FLOW SUPER COMPUTER')
    pages=['🧠 Super Computer','🏠 Dashboard','🇮🇳 VS FLOW India','🌎 VS FLOW Global','⚡ VS FLOW Index','🧬 VS Pattern Lab','🔎 Universal Search','🤖 AI Chart Analyzer','🔥 VS FLOW Core','⚡ VS FLOW Early','🧬 AMD + iFVG','🏆 World-Class Strategy','📡 Master Scanner','🌍 Asset Universe','🔔 Watchlist & Alerts','🛡️ Risk Command','📊 Options & OI','🧪 Quant / Backtest','🎯 VFTC','📓 Trading Journal','⚙️ Settings']
    _target=st.session_state.pop('nav_target',None)
    _default_index=pages.index(_target) if _target in pages else 0
    page=st.radio('NAVIGATION',pages,index=_default_index,key='page');st.divider();st.markdown('**MTF ENGINE**');st.caption('1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M');st.caption('LOCATION → LIQUIDITY → TRIGGER → ENTRY')

logo_b64=base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ''
st.markdown(f'''<div class="hero"><div class="hero-row"><div class="hero-left"><img class="hero-logo" src="data:image/png;base64,{logo_b64}"><div><div class="brand">VS FLOW</div><div class="sub">ALL MARKETS • ONE VISION • TRADE SMARTER • LIVE BETTER</div></div></div><div class="owner"><b>VAIBHAV SHIRSAT</b><span>TRADER • ANALYZER • BUILDER</span></div></div></div>''',unsafe_allow_html=True)

c1,c2,c3=st.columns([6,1.2,1.0]);q=c1.text_input('search','',placeholder='Search any symbol… RELIANCE, NIFTY, BTC, GOLD, AAPL, EURUSD, CRUDE',label_visibility='collapsed');market=c2.selectbox('market',['Auto','India','Global','Crypto','Commodity'],label_visibility='collapsed')
if c3.button('📈 ANALYZE',use_container_width=True) and q:
    st.session_state.asset_query=q;st.session_state.asset_market=market;st.session_state.asset=resolve(q,market);st.session_state.nav_target='🔎 Universal Search';st.rerun()

if page=='🧠 Super Computer':
    render_super_computer()

elif page=='🧬 VS Pattern Lab':
    render_pattern_lab()

elif page=='🔔 Watchlist & Alerts':
    render_watchlist_alerts()

elif page=='🛡️ Risk Command':
    render_risk_command()

if page=='🇮🇳 VS FLOW India':
    india_syms=[x+'.NS' for x in INDIA100]
    benchmarks=[('NIFTY 50','^NSEI'),('NIFTY BANK','^NSEBANK'),('FINNIFTY','^CNXFIN'),('SENSEX','^BSESN'),('INDIA VIX','^INDIAVIX'),('NIFTY MIDCAP','^NSEMDCP50')]
    render_market_dashboard('🇮🇳 VS FLOW INDIA','decision-first Indian market terminal',benchmarks,'INDIA TOP 100',india_syms,'gold')

elif page=='🌎 VS FLOW Global':
    benchmarks=[('S&P 500','^GSPC'),('Nasdaq 100','^IXIC'),('Dow Jones','^DJI'),('Russell 2000','^RUT'),('CBOE VIX','^VIX'),('FTSE 100','^FTSE'),('DAX','^GDAXI'),('CAC 40','^FCHI')]
    render_market_dashboard('🌎 VS FLOW GLOBAL','Global indices • equities • FX • commodities • crypto',benchmarks,'GLOBAL MAJOR STOCKS',GLOBAL_STOCKS,'cyan')
    st.markdown('### ₿ MAJOR CRYPTO MARKET')
    render_universe_cards([(x.replace('-USD',''),x) for x in CRYPTO[:20]],cols=5)
    st.markdown('### 🪙 COMMODITIES')
    render_universe_cards([(x,x) for x in COMMODITIES],cols=4)

elif page=='⚡ VS FLOW Index':
    idx=[('NIFTY 50','^NSEI'),('NIFTY BANK','^NSEBANK'),('FINNIFTY','^CNXFIN'),('SENSEX','^BSESN'),('INDIA VIX','^INDIAVIX'),('NIFTY MIDCAP','^NSEMDCP50')]
    st.markdown('<div class="section-title">⚡ VS FLOW INDEX • INDEX-FIRST COMPUTER TERMINAL</div>',unsafe_allow_html=True)
    pick=st.selectbox('Index',idx,key='index_pick');sym=pick[1];d=fetch(sym,'6mo','1d');ss=structure(d)
    a,b,c,d1,e=st.columns(5);a.metric('LTP',f'{ss.get("close",0):,.2f}' if ss.get('close') else '—');b.metric('REGIME',ss['bias']);c.metric('RSI',f'{ss.get("rsi",0):.1f}' if ss.get('rsi') else '—');d1.metric('EMA18',f'{ss.get("ema18",0):,.2f}' if ss.get('ema18') else '—');e.metric('VS FLOW SCORE',f'{int(ss.get("score",0)*20)}/100')
    fig=chart(fetch(sym,'6mo','1d'),430)
    if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.markdown('### INDEX MARKET SNAPSHOT')
    rows=[]
    for n,s in idx:
        z=structure(fetch(s,'6mo','1d'));rows.append([n,z['bias'],z.get('score',0)*20,round(z.get('rsi',0),1) if z.get('rsi') else '—'])
    st.dataframe(pd.DataFrame(rows,columns=['INDEX','TREND','VS FLOW SCORE','RSI']),use_container_width=True,hide_index=True)
    st.markdown('### INDEX → CORE / EARLY / AMD + iFVG / OPTIONS')
    if st.button('⚡ RUN COMPLETE INDEX ANALYSIS',type='primary',use_container_width=True):
        data,mtf,score=mtf_analysis(sym); core=core_signal(data); early=early_signal(data); amd=amd_state(data.get('1H',pd.DataFrame())); ifvg=ifvg_state(data.get('15M',pd.DataFrame())); st.session_state.index_full=(sym,data,mtf,score,core,early,amd,ifvg)
    if 'index_full' in st.session_state:
        sym,data,mtf,score,core,early,amd,ifvg=st.session_state.index_full
        st.dataframe(mtf,use_container_width=True,hide_index=True);st.success(f'{sym} • MTF {score}/100 • CORE {core[0]} {core[1]}/100 • EARLY {early[0]}/90 • AMD {amd} • iFVG {ifvg}')

elif page=='🏆 World-Class Strategy':
    render_world_class_page()

elif page=='🏠 Dashboard':
    tiles=st.columns(8)
    for c,(n,s) in zip(tiles,[('🇮🇳 NIFTY 50','^NSEI'),('🇮🇳 BANKNIFTY','^NSEBANK'),('🇮🇳 INDIA VIX','^INDIAVIX'),('🇺🇸 S&P 500','^GSPC'),('🇺🇸 NASDAQ','^IXIC'),('₿ BTC','BTC-USD'),('🪙 GOLD','GC=F'),('🛢️ CRUDE','CL=F')]):
        d=fetch(s,'5d','1d');
        if d.empty:html=f'<div class="ticker"><div class="name">{n}</div><div class="px">—</div><div class="small">Data unavailable</div></div>'
        else:
            last=float(d.Close.iloc[-1]);prev=float(d.Close.iloc[-2]) if len(d)>1 else last;chg=(last/prev-1)*100 if prev else 0;html=f'<div class="ticker"><div class="name">{n}</div><div class="px">{last:,.2f}</div><div class="{"up" if chg>=0 else "down"}">{"▲" if chg>=0 else "▼"} {chg:+.2f}%</div></div>'
        c.markdown(html,unsafe_allow_html=True)
    left,right=st.columns([2.1,1])
    with left:
        st.markdown(f'<div class="hero-market"><img src="data:image/png;base64,{logo_b64}"><h2>ONE CLICK • COMPLETE MARKET INTELLIGENCE</h2><p>INDIA • GLOBAL • CRYPTO • COMMODITIES • FOREX • INDICES</p><div class="goldline">SEARCH → MTF → CORE → EARLY → AMD+iFVG → OPTIONS → VFTC</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="icon-grid">'+''.join([f'<div class="icon-item"><div class="i">{i}</div><b>{b}</b><span>{s}</span></div>' for i,b,s in [('🔍','ANALYZE','8 TIMEFRAMES'),('🔥','CORE','VALID SETUP'),('⚡','EARLY','DEVELOPING'),('🧬','AMD+iFVG','LIQUIDITY'),('🏆','WORLD CLASS','STRATEGIES'),('📊','OPTIONS','OI + IV'),('🛡️','RISK','VFTC GATE'),('🎯','VFTC','TRADE PLAN')]])+'</div>',unsafe_allow_html=True)
    with right:
        d=fetch('^NSEI','6mo','1d');s=structure(d);color='green' if 'BULL' in s['bias'] else 'red' if 'BEAR' in s['bias'] else 'gold';st.markdown(f'<div class="panel"><b>📈 NIFTY MARKET REGIME</b><div class="regime-big {color}">{s["bias"]}</div><div class="bullet">• EMA18 / EMA50 / EMA200 structure</div><div class="bullet">• RSI: {s.get("rsi",0):.1f}</div><div class="bullet">• Higher-timeframe context must be confirmed</div></div>',unsafe_allow_html=True)
        if not d.empty:
            fig=chart(d,230)
            if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.markdown('<div class="section-title">TODAY’S BEST SETUPS • QUICK SCAN</div>',unsafe_allow_html=True)
    scan=scan_rows([x+'.NS' for x in INDIA100[:20]]+GLOBAL_STOCKS[:10]+CRYPTO[:5]+COMMODITIES[:3]);st.dataframe(scan.head(12),use_container_width=True,hide_index=True)

elif page=='🔎 Universal Search':
    sym=st.session_state.get('asset',resolve(st.session_state.get('asset_query','NIFTY'),st.session_state.get('asset_market','Auto')))
    st.markdown(f'<div class="section-title">ONE-CLICK COMPLETE ANALYSIS • {sym}</div>',unsafe_allow_html=True)
    if st.button('⚡ ONE-CLICK ALL INFORMATION • 8 TF + CORE + EARLY + AMD+iFVG + WORLD CLASS',type='primary',use_container_width=True):
        with st.spinner('Running complete VS FLOW intelligence across 8 timeframes…'):
            data,mtf,score=mtf_analysis(sym); st.session_state.full={'data':data,'mtf':mtf,'score':score}
    if 'full' in st.session_state:
        obj=st.session_state.full;data,mtf,score=obj['data'],obj['mtf'],obj['score']
        h4=structure(data.get('4H',pd.DataFrame()));h1=structure(data.get('1H',pd.DataFrame()));d1=structure(data.get('1D',pd.DataFrame()));
        core=core_signal(data); early=early_signal(data); amd=amd_state(data.get('1H',pd.DataFrame())); ifvg=ifvg_state(data.get('15M',pd.DataFrame())); e18=eighteen_day_ma(data.get('1D',pd.DataFrame())); wcl=world_class_analysis(data)
        a,b,c,d,e=st.columns(5);a.metric('MTF SCORE',f'{score}/100');b.metric('CORE',core[0]);c.metric('CORE SCORE',f'{core[1]}/100');d.metric('EARLY',f'{early[0]}/90');e.metric('18-DAY MA',e18['state'])
        st.dataframe(mtf,use_container_width=True,hide_index=True)
        summary=pd.DataFrame([
            ['HTF LOCATION',h4['bias'],h4['score']],['1H LIQUIDITY',liquidity(data.get('1H',pd.DataFrame())),'' ],['CORE TRIGGER',core[2],core[1]],['EARLY SETUP',early[1],early[0]],['AMD',amd,''],['iFVG',ifvg,''],['FVG',fvg_state(data.get('15M',pd.DataFrame()))[0],'' ],['WORLD-CLASS CONFLUENCE',f'{wcl.SCORE.mean():.1f}/100',round(float(wcl.SCORE.mean()),1)]
        ],columns=['ENGINE','RESULT','SCORE'])
        st.markdown('### VS FLOW COMPLETE RESULT');st.dataframe(summary,use_container_width=True,hide_index=True)
        st.markdown(f'<div class="panel"><b class="gold">VFTC FINAL RESULT</b><br><br><b>BIAS:</b> {core[0]}<br><b>LOCATION:</b> 4H {h4["bias"]}<br><b>LIQUIDITY:</b> {liquidity(data.get("1H",pd.DataFrame()))}<br><b>TRIGGER:</b> {core[2]}<br><b>AMD:</b> {amd}<br><b>iFVG:</b> {ifvg}<br><b>18-DAY MA:</b> {e18["state"]}<br><b>FINAL:</b> {core[2]}</div>',unsafe_allow_html=True)
        st.markdown('### WORLD-CLASS STRATEGY CONFLUENCE');st.dataframe(wcl,use_container_width=True,hide_index=True)
        st.markdown('### MTF CHARTS');tabs=st.tabs(MTFS)
        for tab,tf in zip(tabs,MTFS):
            with tab:
                dd=data.get(tf,pd.DataFrame()); ss=structure(dd); st.write(f'**{tf}** — {ss["bias"]} | RSI {ss.get("rsi",0):.1f} | Liquidity {liquidity(dd)} | FVG {fvg_state(dd)[0]} | iFVG {ifvg_state(dd)}');fig=chart(dd,330)
                if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        report=summary.copy(); report['SYMBOL']=sym
        xlsx=excel_bytes(report,{'Complete Analysis':report,'MTF':mtf,'World Class':wcl})
        pdf=pdf_bytes(f'VS FLOW Complete Analysis — {sym}',report)
        c1,c2=st.columns(2)
        if xlsx:c1.download_button('⬇️ DOWNLOAD COMPLETE ANALYSIS • EXCEL',xlsx,file_name=f'VS_FLOW_{re.sub(r"[^A-Za-z0-9_-]","_",sym)}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        if pdf:c2.download_button('⬇️ DOWNLOAD COMPLETE ANALYSIS • PDF',pdf,file_name=f'VS_FLOW_{re.sub(r"[^A-Za-z0-9_-]","_",""+sym)}.pdf',mime='application/pdf',use_container_width=True)
    else:st.info('Enter a symbol above and click ANALYZE, then run ONE-CLICK ALL INFORMATION.')

elif page=='🤖 AI Chart Analyzer':
    st.markdown('<div class="section-title">AI CHART ANALYZER • PASTE OR UPLOAD → ANALYZE → VFTC</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel" style="text-align:center"><b style="font-size:22px">📋 PASTE CHART HERE</b><br><span class="small">Chrome / Edge / Safari: copy a chart image, then click Paste. Upload remains available as fallback.</span></div>',unsafe_allow_html=True)
    imgs=[]
    if paste_image:
        try:
            pasted=paste_image(label='📋 PASTE IMAGE FROM CLIPBOARD',key='vsflow_paste')
            if pasted is not None:
                bio=io.BytesIO();pasted.save(bio,format='PNG');imgs.append({'bytes':bio.getvalue(),'mime':'image/png','timeframe':'Unassigned'})
                st.image(pasted,use_container_width=True)
        except Exception as e:st.caption(f'Paste component unavailable: {e}')
    uploads=st.file_uploader('OR UPLOAD 1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M',type=['png','jpg','jpeg','webp'],accept_multiple_files=True)
    for i,f in enumerate(uploads or []):imgs.append({'bytes':f.getvalue(),'mime':f.type,'timeframe':MTFS[min(i,7)]})
    symbol=st.text_input('Symbol / instrument','',key='ai_symbol');model=st.selectbox('AI Model',['gpt-5.6-luna','gpt-5.6-sol'])
    if imgs and st.button('⚡ RUN AI VFTC ANALYSIS',type='primary',use_container_width=True):
        with st.spinner('AI is reading chart evidence…'):st.session_state.ai_result=ai_analyze(imgs,symbol,model)
    if st.session_state.get('ai_result'):st.markdown('<div class="panel">'+st.session_state.ai_result.replace('\n','<br>')+'</div>',unsafe_allow_html=True)

elif page in ['🔥 VS FLOW Core','⚡ VS FLOW Early','🧬 AMD + iFVG']:
    title={'🔥 VS FLOW Core':'VS FLOW CORE SETUP','⚡ VS FLOW Early':'VS FLOW EARLY SETUP','🧬 AMD + iFVG':'AMD + iFVG ENGINE'}[page];st.markdown(f'<div class="section-title">{title}</div>',unsafe_allow_html=True);sym=resolve(st.text_input('Symbol','NIFTY',key='eng_sym'), 'Auto')
    if st.button('🚀 RUN ENGINE • ALL 8 TF',type='primary',use_container_width=True):
        with st.spinner('Fetching MTF data and calculating signals…'):st.session_state.engine=mtf_analysis(sym)
    if 'engine' in st.session_state:
        data,mtf,score=st.session_state.engine;st.dataframe(mtf,use_container_width=True,hide_index=True);core=core_signal(data);early=early_signal(data);st.markdown(f'<div class="panel"><b>CORE</b>: {core[0]} • {core[1]}/100 • {core[2]}<br><b>EARLY</b>: {early[0]}/90 • {early[1]} • {early[2]} • {early[3]}<br><b>AMD+iFVG</b>: AMD {amd_state(data.get("1H",pd.DataFrame()))} • iFVG/FVG {fvg_state(data.get("15M",pd.DataFrame()))[0]}</div>',unsafe_allow_html=True)

elif page=='🏆 World-Class Strategy':
    st.markdown('<div class="section-title">WORLD-CLASS STRATEGY LAB • LIVE SYMBOL ANALYSIS</div>',unsafe_allow_html=True)
    sym=resolve(st.text_input('Symbol / instrument','NIFTY',key='wcl_sym'),'Auto')
    if st.button('🏆 RUN WORLD-CLASS CONFLUENCE',type='primary',use_container_width=True):
        with st.spinner('Evaluating trend, correction, 18-day MA, breakout, quant and volume context…'):
            data=mtf_fetch(sym);st.session_state.wcl=world_class_analysis(data)
    if 'wcl' in st.session_state:
        w=st.session_state.wcl;st.dataframe(w,use_container_width=True,hide_index=True)
        avg=float(w.SCORE.mean()); st.metric('WORLD-CLASS CONFLUENCE SCORE',f'{avg:.1f}/100')
        xlsx=excel_bytes(w,{'World Class':w});pdf=pdf_bytes(f'VS FLOW World-Class Strategy Lab — {sym}',w)
        c1,c2=st.columns(2)
        if xlsx:c1.download_button('⬇️ EXPORT STRATEGY ANALYSIS • EXCEL',xlsx,file_name=f'VS_FLOW_World_Class_{re.sub(r"[^A-Za-z0-9_-]","_",sym)}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        if pdf:c2.download_button('⬇️ EXPORT STRATEGY ANALYSIS • PDF',pdf,file_name=f'VS_FLOW_World_Class_{re.sub(r"[^A-Za-z0-9_-]","_",sym)}.pdf',mime='application/pdf',use_container_width=True)
    else:
        st.info('Select a symbol and run the engine. This lab now produces symbol-specific framework scores, not only a static strategy list.')
        static=pd.DataFrame([['Pau Perdices Bellet','Trend → correction → key level → reversal + risk'],['Inna Rosputnia','18-day MA trend following + systematic discipline'],['Paul Tudor Jones','Capital preservation + asymmetric R:R'],['Richard Dennis','Breakout + ATR risk'],['Jim Simons','Quant validation / systematic testing'],['Darvas','Box breakout'],['Livermore','Trend + winner management'],['Suricate Trading','COT + term structure + volume profile']],columns=['FRAMEWORK','INTEGRATION'])
        st.dataframe(static,use_container_width=True,hide_index=True)

elif page=='📡 Master Scanner':
    st.markdown('<div class="section-title">MASTER SCANNER • INDIA TOP 100 + GLOBAL STOCKS + INDICES + CRYPTO + COMMODITIES</div>',unsafe_allow_html=True)
    cat=st.selectbox('Universe',['India Top 100','Global Major Stocks','Global Major Indices','Major Crypto','Major Commodities','All Markets','Custom'])
    custom=st.text_area('Custom symbols (one per line/comma)','') if cat=='Custom' else ''
    if cat=='India Top 100':syms=[x+'.NS' for x in INDIA100]
    elif cat=='Global Major Stocks':syms=GLOBAL_STOCKS
    elif cat=='Global Major Indices':syms=GLOBAL_INDICES
    elif cat=='Major Crypto':syms=CRYPTO
    elif cat=='Major Commodities':syms=COMMODITIES
    elif cat=='All Markets':syms=[x+'.NS' for x in INDIA100]+GLOBAL_STOCKS+GLOBAL_INDICES+CRYPTO+COMMODITIES
    else:syms=[resolve(x,'Auto') for x in re.split(r'[\n,; ]+',custom) if x]
    syms=list(dict.fromkeys(syms));st.caption(f'{len(syms)} instruments selected. Scan is a candidate engine; final trade requires the full MTF confirmation rule.')
    if st.button('🚀 RUN FULL UNIVERSE SCAN',type='primary',use_container_width=True):
        with st.spinner(f'Scanning {len(syms)} instruments…'):st.session_state.scan=scan_rows(syms)
    if 'scan' in st.session_state:
        scan=st.session_state.scan;st.dataframe(scan,use_container_width=True,hide_index=True,height=560)
        xlsx=excel_bytes(scan,{'Scanner':scan});pdf=pdf_bytes('VS FLOW Master Scanner',scan)
        c1,c2=st.columns(2)
        if xlsx:c1.download_button('⬇️ DOWNLOAD SCANNER • EXCEL',xlsx,file_name='VS_FLOW_Master_Scanner.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        if pdf:c2.download_button('⬇️ DOWNLOAD SCANNER • PDF',pdf,file_name='VS_FLOW_Master_Scanner.pdf',mime='application/pdf',use_container_width=True)

elif page=='🌍 Asset Universe':
    st.markdown('<div class="section-title">COMPLETE ASSET UNIVERSE • ONE PLACE</div>',unsafe_allow_html=True)
    st.caption('Built-in universes are curated. For truly exchange-complete coverage, import your broker/data-vendor symbol master below; the imported list becomes available to the scanner during this session.')
    up=st.file_uploader('IMPORT EXCHANGE / BROKER SYMBOL MASTER (CSV)',type=['csv'],key='universe_csv')
    if up:
        try:
            udf=pd.read_csv(up)
            st.session_state.imported_universe=udf
            st.success(f'Loaded {len(udf):,} rows from {up.name}.')
        except Exception as e:
            st.error(f'Could not read CSV: {e}')
    if 'imported_universe' in st.session_state:
        udf=st.session_state.imported_universe
        st.dataframe(udf.head(1000),use_container_width=True,hide_index=True,height=280)
        symbol_col=st.selectbox('Symbol column',list(udf.columns),key='import_symbol_col')
        imported=[str(x).strip() for x in udf[symbol_col].dropna().tolist() if str(x).strip()]
        if imported and st.button('📡 SCAN IMPORTED UNIVERSE',type='primary',use_container_width=True):
            with st.spinner(f'Scanning {len(imported):,} imported instruments…'): st.session_state.imported_scan=scan_rows(imported)
        if 'imported_scan' in st.session_state: st.dataframe(st.session_state.imported_scan,use_container_width=True,hide_index=True,height=420)
    tabs=st.tabs(['🇮🇳 INDIAN TOP 100','🇮🇳 INDIAN INDICES','🌎 GLOBAL MAJOR STOCKS','📈 GLOBAL INDICES','₿ MAJOR CRYPTO','🪙 COMMODITIES'])
    groups=[([x+'.NS' for x in INDIA100],'Indian Top 100'),(['^NSEI','^NSEBANK','^BSESN','^INDIAVIX','^CNXIT','^CNXPHARMA','^CNXAUTO','^CNXMETAL','^CNXREALTY','^CNXMEDIA','^CNXPSUBANK','^CNXENERGY','^CNXFIN','^CNXFMCG'],'Indian Major Indices'),(GLOBAL_STOCKS,'Global Major Stocks'),(GLOBAL_INDICES,'Global Major Indices'),(CRYPTO,'Major Crypto'),(COMMODITIES,'Major Commodities')]
    for tab,(syms,name) in zip(tabs,groups):
        with tab:
            df=pd.DataFrame({'SYMBOL':syms});st.caption(f'{name}: {len(df)} instruments');st.dataframe(df,use_container_width=True,hide_index=True,height=500)
            if st.button(f'🔎 SCAN {name.upper()}',key='univ_'+name):
                with st.spinner(f'Scanning {len(syms)} instruments…'):st.session_state['univ_'+name]=scan_rows(syms)
            if 'univ_'+name in st.session_state:
                scan=st.session_state['univ_'+name];st.dataframe(scan,use_container_width=True,hide_index=True,height=400)
                xlsx=excel_bytes(scan,{'Universe':scan});pdf=pdf_bytes(f'VS FLOW {name}',scan);c1,c2=st.columns(2)
                if xlsx:c1.download_button('⬇️ EXCEL',xlsx,file_name=f'VS_FLOW_{re.sub(r"[^A-Za-z0-9]","_",name)}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key='x_'+name,use_container_width=True)
                if pdf:c2.download_button('⬇️ PDF',pdf,file_name=f'VS_FLOW_{re.sub(r"[^A-Za-z0-9]","_",name)}.pdf',mime='application/pdf',key='p_'+name,use_container_width=True)

elif page=='📊 Options & OI':
    st.markdown('<div class="section-title">OPTIONS & OI • NSE V3 LIVE CONTEXT</div>',unsafe_allow_html=True)
    st.caption('NSE option-chain access can be rate-limited on cloud servers. If live fetch is blocked, use the official NSE page and import its CSV/JSON. No synthetic OI, PCR or IV is generated.')
    opt_sym=st.selectbox('NSE option chain',['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY','NIFTYNXT50'],key='opt_sym_v6')
    c1,c2=st.columns([3,1]);
    with c1: st.link_button('↗ OPEN OFFICIAL NSE OPTION CHAIN',f'https://www.nseindia.com/option-chain?symbol={opt_sym}',use_container_width=True)
    with c2: fetch_opt=st.button('🔄 FETCH LIVE',type='primary',use_container_width=True)
    if fetch_opt:
        with st.spinner(f'Fetching {opt_sym} option chain + expiry…'):st.session_state.opt=nse_options(opt_sym)
    upload=st.file_uploader('Fallback: upload NSE downloaded .CSV or raw .JSON',type=['csv','json'],key='opt_upload_v6')
    if upload:
        obj,err=parse_option_upload(upload);st.session_state.opt=(obj,err)
    if 'opt' in st.session_state:
        obj,err=st.session_state.opt
        if err:st.error(f'Live option-chain fetch failed: {err}')
        elif obj and not obj['df'].empty:
            df=obj['df'];pcr=float(df.PE_OI.fillna(0).sum()/max(df.CE_OI.fillna(0).sum(),1));mp=max_pain(df);spot=obj.get('spot');
            ivs=pd.concat([df.CE_IV,df.PE_IV],ignore_index=True).dropna() if 'CE_IV' in df and 'PE_IV' in df else pd.Series(dtype=float);atm_iv=float(ivs.mean()) if not ivs.empty else None
            a,b,c,d,e=st.columns(5);a.metric('SPOT',f'{float(spot):,.2f}' if spot else '—');b.metric('PCR',f'{pcr:.2f}');c.metric('MAX PAIN',f'{float(mp):,.0f}' if mp else '—');d.metric('ATM/AVG IV',f'{atm_iv:.2f}' if atm_iv else '—');e.metric('EXPIRY',str(obj.get('expiry') or '—'))
            if spot:
                atm=float(spot);view=df.iloc[(df.strike.astype(float)-atm).abs().argsort()[:15]].sort_values('strike')
            else:view=df.head(30)
            st.dataframe(view,use_container_width=True,hide_index=True,height=560)
            xlsx=excel_bytes(df,{'Option Chain':df});pdf=pdf_bytes(f'VS FLOW Option Chain — {opt_sym}',view);c1,c2=st.columns(2)
            if xlsx:c1.download_button('⬇️ OPTION CHAIN • EXCEL',xlsx,file_name=f'{opt_sym}_Option_Chain.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
            if pdf:c2.download_button('⬇️ OPTION CHAIN • PDF',pdf,file_name=f'{opt_sym}_Option_Chain.pdf',mime='application/pdf',use_container_width=True)
        else:st.warning('No option-chain rows returned. Use the official NSE page and upload its CSV/JSON.')
    else:st.info('Click FETCH LIVE. If NSE blocks the cloud IP, download the chain from NSE and upload the CSV/JSON here. No synthetic OI/PCR/IV is generated.')

elif page=='🧪 Quant / Backtest':
    st.markdown('<div class="section-title">QUANT / BACKTEST LAB</div>',unsafe_allow_html=True);sym=resolve(st.text_input('Backtest symbol','NIFTY'),'Auto');d=fetch(sym,'5y','1d')
    if not d.empty:
        x=enrich(d);sig=x.Close>x.EMA18;ret=x.Close.pct_change().shift(-1);strategy=ret.where(sig,-ret);equity=(1+strategy.fillna(0)).cumprod();c1,c2,c3=st.columns(3);c1.metric('Trades',int(sig.sum()));c2.metric('Avg daily return',f'{strategy.mean()*100:.3f}%');c3.metric('Max drawdown',f'{((equity/equity.cummax())-1).min()*100:.2f}%');st.line_chart(equity)
    else:st.warning('No data for backtest symbol.')

elif page=='🎯 VFTC':
    st.markdown('<div class="section-title">VS FLOW TRADE CARD • VFTC</div>',unsafe_allow_html=True);sym=st.text_input('Symbol','NIFTY');bias=st.selectbox('Bias',['BUY','SELL','WAIT']);entry=st.number_input('Entry',value=0.0);sl=st.number_input('Stop Loss',value=0.0);tp1=st.number_input('TP1',value=0.0);tp2=st.number_input('TP2',value=0.0);score=st.slider('Manual confirmation score',0,100,70);status='WAIT / MONITOR' if score<75 else 'VALID CANDIDATE';
    st.markdown(f'<div class="panel"><b class="gold">{sym} • VFTC FINAL RESULT</b><br><br>1. Analysis Overview<br>2. Bias: <b>{bias}</b><br>3. Confidence: {score}/100<br>4. Entry Zone: {entry if entry else "define after location + trigger"}<br>5. Stop Loss: {sl if sl else "logical invalidation"}<br>6. TP1 / TP2: {tp1 if tp1 else "structure"} / {tp2 if tp2 else "structure"}<br>7. Risk:Reward: calculate from confirmed entry/SL/TP<br>8. Market Context: HTF location first<br>9. Multi-Timeframe Analysis: 1W→1D→4H→1H→30M→15M→5M→1M<br>10. Setup Status: <b>{status}</b><br>11. Invalidation: thesis invalidation level<br>12. Final Result: <b>{status}</b></div>',unsafe_allow_html=True)

elif page=='📓 Trading Journal':
    st.markdown('<div class="section-title">TRADING JOURNAL • EXECUTION HISTORY</div>',unsafe_allow_html=True)
    with st.form('journal_form'):
        a,b,c,d=st.columns(4)
        jdate=a.date_input('Date'); jsym=b.text_input('Symbol','NIFTY'); jsetup=c.selectbox('Setup',['CORE','EARLY','AMD+iFVG','PATTERN','OTHER']); jbias=d.selectbox('Bias',['BUY','SELL','WAIT'])
        e,f,g,h=st.columns(4); jentry=e.number_input('Entry',value=0.0); jsl=f.number_input('SL',value=0.0); jtp=g.number_input('TP',value=0.0); jresult=h.selectbox('Result',['OPEN','WIN','LOSS','BE','WAIT'])
        jlesson=st.text_input('Lesson / notes','')
        submitted=st.form_submit_button('➕ ADD JOURNAL ENTRY',type='primary',use_container_width=True)
    if submitted:
        st.session_state.journal.append({'Date':str(jdate),'Symbol':jsym.upper(),'Setup':jsetup,'Bias':jbias,'Entry':jentry,'SL':jsl,'TP':jtp,'Result':jresult,'Lesson':jlesson})
        st.success('Journal entry added to this session.')
    jdf=pd.DataFrame(st.session_state.journal,columns=['Date','Symbol','Setup','Bias','Entry','SL','TP','Result','Lesson'])
    if jdf.empty: st.info('No journal entries yet. Add the first execution record above.')
    else:
        st.dataframe(jdf,use_container_width=True,hide_index=True,height=460)
        st.download_button('⬇️ EXPORT JOURNAL CSV',jdf.to_csv(index=False).encode('utf-8'),file_name='VS_FLOW_Trading_Journal.csv',mime='text/csv',use_container_width=True)

elif page=='⚙️ Settings':
    st.markdown('<div class="section-title">SETTINGS / DEPLOYMENT STATUS</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><b class="gold">{APP}</b><br>Version: {VERSION}<br>Owner: {AUTHOR}<br>Architecture: India + Global + Index + Pattern Lab + Core + Early + AMD/iFVG + Strategy + Scanner + Options + Quant + VFTC + Journal</div>',unsafe_allow_html=True)
    st.write(f'**Excel export:** {"OK" if Workbook else "NOT INSTALLED"}')
st.write(f'**PDF export:** {"OK" if SimpleDocTemplate else "NOT INSTALLED"}');st.write(f'**Owner:** {AUTHOR}');st.write(f'**yfinance:** {"OK" if yf else "NOT INSTALLED"}');st.write(f'**Plotly:** {"OK" if go else "NOT INSTALLED"}');st.write(f'**Image paste:** {"OK" if paste_image else "INSTALL COMPONENT"}');st.code('OPENAI_API_KEY = "sk-..."',language='toml');st.warning('Never commit API keys to GitHub. Streamlit recommends storing secrets outside the repository and adding them through the app Secrets settings.')

st.markdown('<div class="panel" style="margin-top:18px"><b class="gold">FINAL PLATFORM NOTE</b><br>This release is production-ready as a Streamlit research terminal. Market breadth and security coverage depend on the connected data provider. For exchange-complete universes and low-latency real-time feeds, connect a licensed market-data/broker API rather than relying on synthetic or guessed values.</div>',unsafe_allow_html=True)
st.markdown(f'<div style="margin-top:20px;border-top:1px solid #17374c;padding:9px;color:#688093;font-size:9px">{APP} {VERSION} • {AUTHOR} • ALL MARKETS • ONE VISION • Educational / research use only</div>',unsafe_allow_html=True)
