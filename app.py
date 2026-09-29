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
    from st_img_pastebutton import paste as paste_image
except Exception:
    paste_image = None

BASE=Path(__file__).resolve().parent
LOGO=BASE/'vs_flow_logo.png'
APP='VS FLOW AI MASTER'
VERSION='V5.0'
AUTHOR='VAIBHAV SHIRSAT'
MTFS=['1W','1D','4H','1H','30M','15M','5M','1M']
WEIGHTS={'1W':15,'1D':20,'4H':20,'1H':15,'30M':10,'15M':8,'5M':10,'1M':2}

POPULAR={
'NIFTY':'^NSEI','NIFTY50':'^NSEI','BANKNIFTY':'^NSEBANK','SENSEX':'^BSESN','INDIAVIX':'^INDIAVIX',
'SPX':'^GSPC','S&P500':'^GSPC','NASDAQ':'^IXIC','DOW':'^DJI','DAX':'^GDAXI','FTSE':'^FTSE','NIKKEI':'^N225','HANGSENG':'^HSI','CAC40':'^FCHI','ASX200':'^AXJO','KOSPI':'^KS11','SSE':'000001.SS','CSI300':'000300.SS','NIFTYIT':'^CNXIT','NIFTYBANK':'^NSEBANK',
'BTC':'BTC-USD','BTCUSD':'BTC-USD','ETH':'ETH-USD','SOL':'SOL-USD','XRP':'XRP-USD','BNB':'BNB-USD','DOGE':'DOGE-USD','ADA':'ADA-USD','AVAX':'AVAX-USD','LINK':'LINK-USD','DOT':'DOT-USD','TRX':'TRX-USD',
'GOLD':'GC=F','SILVER':'SI=F','CRUDE':'CL=F','WTI':'CL=F','NATGAS':'NG=F','COPPER':'HG=F','PLATINUM':'PL=F','PALLADIUM':'PA=F','USDINR':'INR=X','EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'JPY=X'
}
INDIA100='''RELIANCE TCS HDFCBANK ICICIBANK BHARTIARTL INFY SBIN LT ITC HINDUNILVR AXISBANK KOTAKBANK M&M MARUTI SUNPHARMA HCLTECH BAJFINANCE TITAN ULTRACEMCO ADANIENT ADANIPORTS NTPC ONGC POWERGRID JSWSTEEL TATASTEEL WIPRO NESTLEIND ASIANPAINT TECHM TATAMOTORS EICHERMOT COALINDIA BAJAJFINSV GRASIM HINDALCO DIVISLAB DRREDDY CIPLA APOLLOHOSP HEROMOTOCO BPCL BRITANNIA TATACONSUM INDUSINDBK SHRIRAMFIN BEL TRENT ZOMATO JIOFIN IRCTC PIDILITIND DLF LODHA SIEMENS ABB VEDL HAL BHEL IOC GAIL BANKBARODA CANBK PNB UNIONBANK IDFCFIRSTB INDIAMART DMART TVSMOTOR BOSCHLTD MOTHERSON VBL DABUR MARICO GODREJCP COLPAL SBICARD ICICIPRULI CHOLAFIN MUTHOOTFIN OFSS LTIM LTTS PERSISTENT MPHASIS COFORGE CUMMINSIND VOLTAS AMBER APLAPOLLO AUROPHARMA LUPIN TORNTPHARM BIOCON SRF PIIND ASTRAL CONCOR NHPC SJVN IEX DIXON'''.split()
GLOBAL_STOCKS='''AAPL MSFT NVDA AMZN GOOGL META AVGO TSLA BRK-B JPM WMT ORCL COST NFLX AMD CRM INTC QCOM MU TXN AMAT NOW ADBE INTU ISRG LLY NVO UNH JNJ PG KO PEP XOM CVX COP CAT GE BA RTX HON UBER SHOP PLTR BABA TSM ASML SAP SONY TM NVS RY HSBC TD BHP RIO SHEL'''.split()
GLOBAL_INDICES=['^GSPC','^IXIC','^DJI','^RUT','^GDAXI','^FTSE','^FCHI','^N225','^HSI','^KS11','^AXJO','^STOXX50E','^BSESN','^NSEI','^NSEBANK','^CNXIT','^INDIAVIX']
CRYPTO=['BTC-USD','ETH-USD','SOL-USD','BNB-USD','XRP-USD','DOGE-USD','ADA-USD','AVAX-USD','LINK-USD','DOT-USD','TRX-USD','SHIB-USD','LTC-USD','BCH-USD','UNI-USD','ATOM-USD','NEAR-USD','APT-USD','SUI-USD','ICP-USD','FIL-USD','ETC-USD','HBAR-USD','XLM-USD','MATIC-USD']
COMMODITIES=['GC=F','SI=F','CL=F','BZ=F','NG=F','HG=F','PL=F','PA=F','ZC=F','ZS=F','ZW=F']

st.set_page_config(page_title=f'{APP} • {AUTHOR}',page_icon='⚡',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
:root{--bg:#02070d;--panel:#06111d;--line:#22445b;--gold:#ffd34e;--green:#00f29a;--red:#ff405b;--cyan:#10dcff;--muted:#91a9ba;--white:#f7fbff}
.stApp{background:radial-gradient(circle at 72% 8%,rgba(0,180,255,.12),transparent 25%),radial-gradient(circle at 15% 0%,rgba(255,184,0,.10),transparent 28%),linear-gradient(180deg,#01050a 0%,#020914 55%,#01050a 100%);color:var(--white)}
.block-container{max-width:1900px;padding:1.1rem 1rem 2.2rem!important}.hero{min-height:108px;box-sizing:border-box;border:1px solid #735a1e;border-radius:18px;padding:10px 18px;background:linear-gradient(100deg,rgba(2,8,15,.98),rgba(10,22,34,.96));box-shadow:0 0 35px rgba(255,194,0,.06);margin:0 0 12px;overflow:visible}.hero-row{min-height:84px;display:flex;align-items:center;justify-content:space-between;gap:20px}.hero-left{display:flex;align-items:center;gap:16px;min-width:0}.hero-logo{width:82px;height:82px;flex:0 0 82px;border-radius:50%;object-fit:cover;border:1px solid #c99c2d;box-shadow:0 0 24px rgba(255,202,61,.20)}.brand{font-size:38px;font-weight:1000;letter-spacing:-1.5px;background:linear-gradient(90deg,#fff0a2,#ffd43c,#f2b31c);-webkit-background-clip:text;color:transparent;line-height:1.05;white-space:nowrap}.sub{color:#c0ced7;font-size:10px;letter-spacing:3px;margin-top:6px;white-space:nowrap}.owner{text-align:right;white-space:nowrap}.owner b{font-size:18px;color:#ffe07a}.owner span{display:block;color:#91a8b8;font-size:9px;letter-spacing:2px;margin-top:5px}
.stButton button{background:linear-gradient(180deg,#132c3e,#071522)!important;border:1px solid #315873!important;color:#fff!important;border-radius:9px!important;font-weight:800!important}.stButton button:hover{border-color:var(--gold)!important;box-shadow:0 0 18px rgba(255,211,78,.16)}.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div{background:#04101b!important;color:#fff!important;border:1px solid #204861!important;border-radius:8px!important}.searchbar{border:1px solid #6f581b;border-radius:18px;padding:7px;background:#06111b}
.ticker{background:linear-gradient(145deg,#06131f,#04101a);border:1px solid #1f455b;border-radius:9px;padding:8px 10px;min-height:78px}.ticker .name{font-size:10px;color:#b7c8d2;font-weight:800}.ticker .px{font-size:17px;font-weight:900;margin-top:3px}.up{color:var(--green)}.down{color:var(--red)}.section-title{font-size:18px;font-weight:950;letter-spacing:.4px;margin:12px 0 6px}.panel{background:linear-gradient(145deg,rgba(7,20,32,.97),rgba(3,11,19,.97));border:1px solid #1d4358;border-radius:14px;padding:12px;box-shadow:inset 0 1px rgba(255,255,255,.02),0 8px 25px rgba(0,0,0,.15)}
.hero-market{min-height:360px;background:radial-gradient(circle at 50% 45%,rgba(0,225,170,.10),transparent 22%),radial-gradient(circle at 35% 50%,rgba(0,170,255,.14),transparent 28%),linear-gradient(145deg,#03121b,#020914 70%);border:1px solid #1b536a;border-radius:14px;padding:12px;text-align:center;overflow:hidden}.hero-market img{width:min(330px,62%);opacity:.92;filter:drop-shadow(0 0 22px rgba(255,198,44,.14));margin-top:8px}.hero-market h2{margin:0;color:#fff;font-size:22px;letter-spacing:2px}.hero-market p{color:#9eb4c3;font-size:10px;letter-spacing:2px;margin:5px 0}.goldline{color:#ffd65b;font-size:11px;letter-spacing:2px;margin-top:4px}.metric-card{background:linear-gradient(145deg,#071827,#04101a);border:1px solid #1d4258;border-radius:10px;padding:10px}.metric-card .k{font-size:9px;color:#92aaba;text-transform:uppercase;letter-spacing:1px}.metric-card .v{font-size:19px;font-weight:950;margin-top:3px}.small{font-size:10px;color:#8fa9ba}.gold{color:#ffd76a}.green{color:#00ef9b}.red{color:#ff6478}.cyan{color:#22e0ff}.setup-row{display:grid;grid-template-columns:1.1fr .7fr 1.1fr .7fr .5fr;gap:6px;padding:7px 8px;border-bottom:1px solid #153448;font-size:10px;align-items:center}.setup-row.head{color:#91a9b8;font-weight:900}.badge{padding:3px 7px;border-radius:5px;font-weight:900;font-size:10px;display:inline-block}.buy{background:rgba(0,242,154,.13);color:#00f29a;border:1px solid rgba(0,242,154,.25)}.sell{background:rgba(255,64,91,.13);color:#ff687b;border:1px solid rgba(255,64,91,.25)}.score{background:#0d5d3f;color:#8bffcb;border-radius:5px;padding:3px 7px;font-weight:900;text-align:center}.regime-big{font-size:22px;font-weight:1000;margin:6px 0 12px}.bullet{font-size:12px;margin:9px 0;color:#cbd7de}.icon-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:8px}.icon-item{border:1px solid #244a60;border-radius:10px;padding:10px;text-align:center;background:#04101a}.icon-item .i{font-size:22px}.icon-item b{font-size:10px;display:block;margin-top:5px}.icon-item span{font-size:8px;color:#8fa9ba}div[data-testid="stDataFrame"]{border:1px solid #1d4258;border-radius:10px;overflow:hidden}footer{visibility:hidden}
@media(max-width:1000px){.hero{min-height:125px}.hero-row{align-items:center}.brand{font-size:28px}.hero-logo{width:70px;height:70px;flex-basis:70px}.owner b{font-size:14px}.icon-grid{grid-template-columns:repeat(2,1fr)}}
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
    x=enrich(d).tail(180);fig=go.Figure();fig.add_trace(go.Candlestick(x=x.index,open=x.Open,high=x.High,low=x.Low,close=x.Close,name='Price',increasing_line_color='#00ef9b',decreasing_line_color='#ff405b'))
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

def nse_options(symbol='NIFTY'):
    if requests is None:return None,'requests unavailable'
    try:
        s=requests.Session();headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36','Accept':'application/json,text/plain,*/*','Referer':'https://www.nseindia.com/'};s.headers.update(headers);s.get('https://www.nseindia.com',timeout=8);url=f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}' if symbol in ['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY'] else f'https://www.nseindia.com/api/option-chain-equities?symbol={symbol}';r=s.get(url,timeout=10);r.raise_for_status();j=r.json();rows=j.get('records',{}).get('data',[]);spot=j.get('records',{}).get('underlyingValue');exp=j.get('records',{}).get('expiryDates',[]);data=[]
        for z in rows:
            ce=z.get('CE',{});pe=z.get('PE',{});data.append({'strike':z.get('strikePrice'),'CE_OI':ce.get('openInterest',0),'PE_OI':pe.get('openInterest',0),'CE_IV':ce.get('impliedVolatility'),'PE_IV':pe.get('impliedVolatility'),'CE_LTP':ce.get('lastPrice'),'PE_LTP':pe.get('lastPrice')})
        df=pd.DataFrame(data).dropna(subset=['strike']);return {'spot':spot,'expiry':exp[0] if exp else None,'df':df},None
    except Exception as e:return None,str(e)

def max_pain(df):
    if df is None or df.empty:return None
    strikes=df['strike'].astype(float).values;best=None
    for s in strikes:
        call=((s-strikes).clip(min=0)*df.CE_OI.fillna(0)).sum();put=((strikes-s).clip(min=0)*df.PE_OI.fillna(0)).sum();pain=call+put
        if best is None or pain<best[1]:best=(s,pain)
    return best[0] if best else None

# sidebar
with st.sidebar:
    if LOGO.exists():st.image(str(LOGO),use_container_width=True)
    st.markdown('### ⚡ VS FLOW AI MASTER V5')
    pages=['🏠 Dashboard','🔎 Universal Search','🤖 AI Chart Analyzer','🔥 VS FLOW Core','⚡ VS FLOW Early','🧬 AMD + iFVG','🏆 World-Class Strategy','📡 Master Scanner','🌍 Asset Universe','📊 Options & OI','🧪 Quant / Backtest','🎯 VFTC','📓 Trading Journal','⚙️ Settings']
    _target=st.session_state.pop('nav_target',None)
    _default_index=pages.index(_target) if _target in pages else 0
    page=st.radio('NAVIGATION',pages,index=_default_index,key='page');st.divider();st.markdown('**MTF ENGINE**');st.caption('1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M');st.caption('LOCATION → LIQUIDITY → TRIGGER → ENTRY')

logo_b64=base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ''
st.markdown(f'''<div class="hero"><div class="hero-row"><div class="hero-left"><img class="hero-logo" src="data:image/png;base64,{logo_b64}"><div><div class="brand">VS FLOW</div><div class="sub">ALL MARKETS • ONE VISION • TRADE SMARTER • LIVE BETTER</div></div></div><div class="owner"><b>VAIBHAV SHIRSAT</b><span>TRADER • ANALYZER • BUILDER</span></div></div></div>''',unsafe_allow_html=True)

c1,c2,c3=st.columns([6,1.2,1.0]);q=c1.text_input('search','',placeholder='Search any symbol… RELIANCE, NIFTY, BTC, GOLD, AAPL, EURUSD, CRUDE',label_visibility='collapsed');market=c2.selectbox('market',['Auto','India','Global','Crypto','Commodity'],label_visibility='collapsed')
if c3.button('📈 ANALYZE',use_container_width=True) and q:
    st.session_state.asset_query=q;st.session_state.asset_market=market;st.session_state.asset=resolve(q,market);st.session_state.nav_target='🔎 Universal Search';st.rerun()

if page=='🏠 Dashboard':
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
    sym=st.session_state.get('asset',resolve(st.session_state.get('asset_query','NIFTY'),st.session_state.get('asset_market','Auto')));st.markdown(f'<div class="section-title">COMPLETE ANALYSIS • {sym}</div>',unsafe_allow_html=True)
    if st.button('⚡ ONE-CLICK FULL ANALYSIS',type='primary',use_container_width=True):
        with st.spinner('Running 8-timeframe VS FLOW engine…'):st.session_state.full=mtf_analysis(sym)
    if 'full' in st.session_state:
        data,mtf,score=st.session_state.full;st.dataframe(mtf,use_container_width=True,hide_index=True);a,b,c,d=st.columns(4);h4=structure(data['4H']);direction,core_score,status=core_signal(data);early,amd,liq,fvg=early_signal(data);a.metric('MTF SCORE',f'{score}/100');b.metric('CORE',direction);c.metric('CORE SCORE',core_score);d.metric('EARLY',early);st.markdown(f'<div class="panel"><b class="gold">VS FLOW COMPLETE READ</b><br><br>LOCATION: 4H {h4["bias"]}<br>LIQUIDITY: {liq}<br>TRIGGER: {"CONFIRMATION PRESENT" if core_score>=75 else "WAIT FOR BOS/CHoCH + RETEST"}<br>AMD: {amd}<br>iFVG/FVG: {fvg}<br><b>FINAL: {status}</b></div>',unsafe_allow_html=True)
        tabs=st.tabs(MTFS)
        for tab,tf in zip(tabs,MTFS):
            with tab:
                dd=data.get(tf,pd.DataFrame());ss=structure(dd);st.write(f'**{tf}** — {ss["bias"]} | RSI {ss.get("rsi",0):.1f} | Liquidity {liquidity(dd)} | FVG {fvg_state(dd)[0]}');fig=chart(dd,360)
                if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    else:st.info('Enter a symbol above, then click ANALYZE or ONE-CLICK FULL ANALYSIS.')

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
    st.markdown('<div class="section-title">WORLD-CLASS STRATEGY LAB</div>',unsafe_allow_html=True);st.dataframe(pd.DataFrame([['Pau Perdices Bellet','Trend → correction → key level → reversal + risk'],['Inna Rosputnia','18-day MA trend following + systematic discipline'],['Paul Tudor Jones','Capital preservation + asymmetric R:R'],['Richard Dennis','Breakout + ATR risk'],['Jim Simons','Quant validation / systematic testing'],['Darvas','Box breakout'],['Livermore','Trend + winner management'],['Suricate Trading','COT + term structure + volume profile']],columns=['FRAMEWORK','INTEGRATION']),use_container_width=True,hide_index=True)

elif page=='📡 Master Scanner':
    st.markdown('<div class="section-title">MASTER SCANNER • INDIA + GLOBAL + CRYPTO + COMMODITIES + INDICES</div>',unsafe_allow_html=True);cat=st.selectbox('Universe',['India Top 100','Global Major Stocks','Global Major Indices','Major Crypto','Major Commodities','Custom']);custom=st.text_area('Custom symbols (one per line/comma)','') if cat=='Custom' else ''
    if cat=='India Top 100':syms=[x+'.NS' for x in INDIA100]
    elif cat=='Global Major Stocks':syms=GLOBAL_STOCKS
    elif cat=='Global Major Indices':syms=GLOBAL_INDICES
    elif cat=='Major Crypto':syms=CRYPTO
    elif cat=='Major Commodities':syms=COMMODITIES
    else:syms=[resolve(x,'Auto') for x in re.split(r'[\n,; ]+',custom) if x]
    st.caption(f'{len(syms)} instruments selected • batch scan uses daily data first, then use One-Click Full Analysis on candidates.')
    if st.button('🚀 RUN FULL UNIVERSE SCAN',type='primary',use_container_width=True):
        with st.spinner(f'Scanning {len(syms)} instruments…'):st.session_state.scan=scan_rows(syms)
    if 'scan' in st.session_state:st.dataframe(st.session_state.scan,use_container_width=True,hide_index=True)

elif page=='🌍 Asset Universe':
    st.markdown('<div class="section-title">ALL MARKETS • COMPLETE UNIVERSE</div>',unsafe_allow_html=True);tabs=st.tabs(['🇮🇳 INDIA TOP 100','🌎 GLOBAL STOCKS','📈 GLOBAL INDICES','₿ CRYPTO','🪙 COMMODITIES'])
    groups=[([x+'.NS' for x in INDIA100],'India Top 100'),(GLOBAL_STOCKS,'Global Major Stocks'),(GLOBAL_INDICES,'Global Major Indices'),(CRYPTO,'Major Crypto'),(COMMODITIES,'Major Commodities')]
    for tab,(syms,name) in zip(tabs,groups):
        with tab:
            df=pd.DataFrame({'SYMBOL':syms});st.dataframe(df,use_container_width=True,hide_index=True,height=520)

elif page=='📊 Options & OI':
    st.markdown('<div class="section-title">OPTIONS & OI • LIVE CONTEXT LAYER</div>',unsafe_allow_html=True);opt_sym=st.selectbox('NSE option chain',['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY']);
    if st.button('🔄 FETCH LIVE NSE OPTION CHAIN',type='primary',use_container_width=True):
        with st.spinner('Fetching NSE option chain…'):st.session_state.opt=nse_options(opt_sym)
    if 'opt' in st.session_state:
        obj,err=st.session_state.opt
        if err:st.error(f'Option chain unavailable: {err}. NSE can rate-limit automated requests; retry later.')
        else:
            df=obj['df'];pcr=df.PE_OI.sum()/max(df.CE_OI.sum(),1);mp=max_pain(df);atm=float(obj['spot']) if obj.get('spot') else None;atm_iv=None
            if atm is not None and not df.empty:
                near=df.iloc[(df.strike.astype(float)-atm).abs().argsort()[:2]];atm_iv=float(pd.concat([near.CE_IV,near.PE_IV]).dropna().mean()) if not pd.concat([near.CE_IV,near.PE_IV]).dropna().empty else None
            a,b,c,d=st.columns(4);a.metric('SPOT',f'{atm:,.2f}' if atm else '—');b.metric('PCR',f'{pcr:.2f}');c.metric('MAX PAIN',f'{mp:,.0f}' if mp else '—');d.metric('ATM IV',f'{atm_iv:.2f}' if atm_iv else '—');st.dataframe(df,use_container_width=True,hide_index=True)
    else:st.info('Click FETCH LIVE NSE OPTION CHAIN. This module does not fabricate PCR/OI/IV values.')

elif page=='🧪 Quant / Backtest':
    st.markdown('<div class="section-title">QUANT / BACKTEST LAB</div>',unsafe_allow_html=True);sym=resolve(st.text_input('Backtest symbol','NIFTY'),'Auto');d=fetch(sym,'5y','1d')
    if not d.empty:
        x=enrich(d);sig=x.Close>x.EMA18;ret=x.Close.pct_change().shift(-1);strategy=ret.where(sig,-ret);equity=(1+strategy.fillna(0)).cumprod();c1,c2,c3=st.columns(3);c1.metric('Trades',int(sig.sum()));c2.metric('Avg daily return',f'{strategy.mean()*100:.3f}%');c3.metric('Max drawdown',f'{((equity/equity.cummax())-1).min()*100:.2f}%');st.line_chart(equity)
    else:st.warning('No data for backtest symbol.')

elif page=='🎯 VFTC':
    st.markdown('<div class="section-title">VS FLOW TRADE CARD • VFTC</div>',unsafe_allow_html=True);sym=st.text_input('Symbol','NIFTY');bias=st.selectbox('Bias',['BUY','SELL','WAIT']);entry=st.number_input('Entry',value=0.0);sl=st.number_input('Stop Loss',value=0.0);tp1=st.number_input('TP1',value=0.0);tp2=st.number_input('TP2',value=0.0);score=st.slider('Manual confirmation score',0,100,70);status='WAIT / MONITOR' if score<75 else 'VALID CANDIDATE';
    st.markdown(f'<div class="panel"><b class="gold">{sym} • VFTC FINAL RESULT</b><br><br>1. Analysis Overview<br>2. Bias: <b>{bias}</b><br>3. Confidence: {score}/100<br>4. Entry Zone: {entry if entry else "define after location + trigger"}<br>5. Stop Loss: {sl if sl else "logical invalidation"}<br>6. TP1 / TP2: {tp1 if tp1 else "structure"} / {tp2 if tp2 else "structure"}<br>7. Risk:Reward: calculate from confirmed entry/SL/TP<br>8. Market Context: HTF location first<br>9. Multi-Timeframe Analysis: 1W→1D→4H→1H→30M→15M→5M→1M<br>10. Setup Status: <b>{status}</b><br>11. Invalidation: thesis invalidation level<br>12. Final Result: <b>{status}</b></div>',unsafe_allow_html=True)

elif page=='📓 Trading Journal':
    st.markdown('<div class="section-title">TRADING JOURNAL</div>',unsafe_allow_html=True);st.info('Use this as an execution log. Export/persistence can be added later; no fake performance is generated.')
    st.dataframe(pd.DataFrame(columns=['Date','Symbol','Setup','Bias','Entry','SL','TP','Risk','Result','Lesson']),use_container_width=True,hide_index=True)

elif page=='⚙️ Settings':
    st.markdown('<div class="section-title">SETTINGS / DATA STATUS</div>',unsafe_allow_html=True);st.write(f'**Version:** {VERSION}');st.write(f'**Owner:** {AUTHOR}');st.write(f'**yfinance:** {"OK" if yf else "NOT INSTALLED"}');st.write(f'**Plotly:** {"OK" if go else "NOT INSTALLED"}');st.write(f'**Image paste:** {"OK" if paste_image else "INSTALL COMPONENT"}');st.code('OPENAI_API_KEY = "sk-..."',language='toml');st.warning('Never commit API keys to GitHub. Streamlit recommends storing secrets outside the repository and adding them through the app Secrets settings.')

st.markdown(f'<div style="margin-top:20px;border-top:1px solid #17374c;padding:9px;color:#688093;font-size:9px">{APP} {VERSION} • {AUTHOR} • ALL MARKETS • ONE VISION • Educational / research use only</div>',unsafe_allow_html=True)
