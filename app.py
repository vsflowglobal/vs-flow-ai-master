import os, re, base64, math
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

BASE = Path(__file__).resolve().parent
LOGO = BASE / 'vs_flow_logo.png'
APP = 'VS FLOW AI MASTER'
VERSION = 'V4.0'
AUTHOR = 'VAIBHAV SHIRSAT'

POPULAR = {
    'NIFTY':'^NSEI','NIFTY50':'^NSEI','BANKNIFTY':'^NSEBANK','SENSEX':'^BSESN','INDIAVIX':'^INDIAVIX',
    'SPX':'^GSPC','S&P500':'^GSPC','NASDAQ':'^IXIC','DOW':'^DJI','DAX':'^GDAXI','FTSE':'^FTSE','NIKKEI':'^N225','HANGSENG':'^HSI',
    'BTC':'BTC-USD','BTCUSD':'BTC-USD','ETH':'ETH-USD','ETHUSD':'ETH-USD','SOL':'SOL-USD','XRP':'XRP-USD',
    'GOLD':'GC=F','SILVER':'SI=F','CRUDE':'CL=F','WTI':'CL=F','NATGAS':'NG=F','USDINR':'INR=X','EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X'
}

st.set_page_config(page_title=f'{APP} • {AUTHOR}', page_icon='⚡', layout='wide', initial_sidebar_state='expanded')

st.markdown('''
<style>
:root{--bg:#02070d;--panel:#06111d;--panel2:#091a29;--line:#22445b;--gold:#ffd34e;--gold2:#ffb400;--green:#00f29a;--red:#ff405b;--cyan:#10dcff;--muted:#91a9ba;--white:#f7fbff}
.stApp{background:radial-gradient(circle at 72% 8%,rgba(0,180,255,.12),transparent 25%),radial-gradient(circle at 15% 0%,rgba(255,184,0,.10),transparent 28%),linear-gradient(180deg,#01050a 0%,#020914 55%,#01050a 100%);color:var(--white)}
.block-container{max-width:1900px;padding:.5rem 1rem 2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#020812,#030a12);border-right:1px solid #1a3548}
[data-testid="stSidebar"] .stButton button{width:100%}
.stButton button{background:linear-gradient(180deg,#132c3e,#071522)!important;border:1px solid #315873!important;color:#fff!important;border-radius:9px!important;font-weight:800!important}
.stButton button:hover{border-color:var(--gold)!important;box-shadow:0 0 18px rgba(255,211,78,.16)}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div{background:#04101b!important;color:#fff!important;border:1px solid #204861!important;border-radius:8px!important}
.hero{border:1px solid #735a1e;border-radius:18px;padding:10px 18px;background:linear-gradient(100deg,rgba(2,8,15,.96),rgba(10,22,34,.94));box-shadow:0 0 35px rgba(255,194,0,.06);margin-bottom:10px}
.hero-row{display:flex;align-items:center;justify-content:space-between;gap:20px}.hero-left{display:flex;align-items:center;gap:16px}.hero-logo{width:74px;height:74px;border-radius:50%;object-fit:cover;border:1px solid #c99c2d;box-shadow:0 0 24px rgba(255,202,61,.20)}
.brand{font-size:36px;font-weight:1000;letter-spacing:-1.5px;background:linear-gradient(90deg,#fff0a2,#ffd43c,#f2b31c);-webkit-background-clip:text;color:transparent;line-height:1}.sub{color:#c0ced7;font-size:10px;letter-spacing:3px;margin-top:5px}.owner{text-align:right}.owner b{font-size:16px;color:#ffe07a}.owner span{display:block;color:#91a8b8;font-size:9px;letter-spacing:2px;margin-top:3px}
.searchbar{border:1px solid #6f581b;border-radius:18px;padding:7px;background:linear-gradient(180deg,#0a1a27,#06111b);box-shadow:0 0 22px rgba(255,194,0,.07)}
.ticker{background:linear-gradient(145deg,#06131f,#04101a);border:1px solid #1f455b;border-radius:9px;padding:8px 10px;min-height:78px}.ticker .name{font-size:10px;color:#b7c8d2;font-weight:800}.ticker .px{font-size:17px;font-weight:900;margin-top:3px}.up{color:var(--green)}.down{color:var(--red)}
.section-title{font-size:18px;font-weight:950;letter-spacing:.4px;margin:12px 0 6px}.panel{background:linear-gradient(145deg,rgba(7,20,32,.97),rgba(3,11,19,.97));border:1px solid #1d4358;border-radius:14px;padding:12px;box-shadow:inset 0 1px rgba(255,255,255,.02),0 8px 25px rgba(0,0,0,.15)}
.hero-market{min-height:360px;background:radial-gradient(circle at 50% 45%,rgba(0,225,170,.10),transparent 22%),radial-gradient(circle at 35% 50%,rgba(0,170,255,.14),transparent 28%),linear-gradient(145deg,#03121b,#020914 70%);border:1px solid #1b536a;border-radius:14px;padding:12px;text-align:center;position:relative;overflow:hidden}.hero-market img{width:min(300px,62%);opacity:.9;filter:drop-shadow(0 0 22px rgba(255,198,44,.14));margin-top:10px}.hero-market h2{margin:0;color:#fff;font-size:22px;letter-spacing:2px}.hero-market p{color:#9eb4c3;font-size:10px;letter-spacing:2px;margin:5px 0}.hero-market .goldline{color:#ffd65b;font-size:11px;letter-spacing:2px;margin-top:4px}
.regime{min-height:360px}.regime-big{font-size:22px;font-weight:1000;margin:6px 0 12px}.bullet{font-size:12px;margin:9px 0;color:#cbd7de}.dotg{color:var(--green)}.doty{color:var(--gold)}.dotr{color:var(--red)}
.setup-row{display:grid;grid-template-columns:1.1fr .7fr 1.1fr .7fr .5fr;gap:6px;padding:7px 8px;border-bottom:1px solid #153448;font-size:10px;align-items:center}.setup-row.head{color:#91a9b8;font-weight:900}.badge{padding:3px 7px;border-radius:5px;font-weight:900;font-size:10px;display:inline-block}.buy{background:rgba(0,242,154,.13);color:#00f29a;border:1px solid rgba(0,242,154,.25)}.sell{background:rgba(255,64,91,.13);color:#ff687b;border:1px solid rgba(255,64,91,.25)}.score{background:#0d5d3f;color:#8bffcb;border-radius:5px;padding:3px 7px;font-weight:900;text-align:center}
.metric-card{background:linear-gradient(145deg,#071827,#04101a);border:1px solid #1d4258;border-radius:10px;padding:10px}.metric-card .k{font-size:9px;color:#92aaba;text-transform:uppercase;letter-spacing:1px}.metric-card .v{font-size:19px;font-weight:950;margin-top:3px}.metric-card .d{font-size:10px;margin-top:2px}
.icon-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px}.icon-item{border:1px solid #244a60;border-radius:10px;padding:10px;text-align:center;background:#04101a}.icon-item .i{font-size:22px}.icon-item b{font-size:10px;display:block;margin-top:5px}.icon-item span{font-size:8px;color:#8fa9ba}
.small{font-size:10px;color:#8fa9ba}.gold{color:#ffd76a}.cyan{color:#22e0ff}.green{color:#00ef9b}.red{color:#ff6478}
div[data-testid="stDataFrame"]{border:1px solid #1d4258;border-radius:10px;overflow:hidden}
footer{visibility:hidden}
@media(max-width:900px){.hero-row{flex-direction:column;align-items:flex-start}.owner{text-align:left}.icon-grid{grid-template-columns:repeat(2,1fr)}}
</style>
''', unsafe_allow_html=True)


def resolve(q, market='Auto'):
    q=q.strip().upper()
    if q in POPULAR:return POPULAR[q]
    if q.endswith(('.NS','.BO','.L','.DE','.HK','.TO')) or '=' in q or q.startswith('^'):return q
    if market=='India':return q+'.NS'
    if market=='Crypto':return q+'-USD'
    return q

@st.cache_data(ttl=90, show_spinner=False)
def fetch(symbol, period='1mo', interval='1d'):
    if yf is None:return pd.DataFrame()
    try:
        d=yf.download(symbol,period=period,interval=interval,auto_adjust=False,progress=False,threads=False)
        if d is None or d.empty:return pd.DataFrame()
        if isinstance(d.columns,pd.MultiIndex):d.columns=d.columns.get_level_values(0)
        d.columns=[str(x).title() for x in d.columns]
        return d.dropna(how='all')
    except Exception:return pd.DataFrame()

def rsi(s,n=14):
    d=s.diff();up=d.clip(lower=0);dn=-d.clip(upper=0)
    rs=up.ewm(alpha=1/n,adjust=False).mean()/dn.ewm(alpha=1/n,adjust=False).mean().replace(0,np.nan)
    return 100-100/(1+rs)

def enrich(d):
    x=d.copy()
    if x.empty:return x
    x['EMA18']=x.Close.ewm(span=18,adjust=False).mean();x['EMA20']=x.Close.ewm(span=20,adjust=False).mean();x['EMA50']=x.Close.ewm(span=50,adjust=False).mean();x['EMA200']=x.Close.ewm(span=200,adjust=False).mean();x['RSI']=rsi(x.Close)
    tr=pd.concat([x.High-x.Low,(x.High-x.Close.shift()).abs(),(x.Low-x.Close.shift()).abs()],axis=1).max(axis=1);x['ATR']=tr.rolling(14).mean()
    x['VMA20']=x.Volume.rolling(20).mean() if 'Volume' in x else np.nan;x['VOLR']=x.Volume/x.VMA20 if 'Volume' in x else np.nan
    return x

def structure(d):
    if d.empty:return {'bias':'NO DATA','score':0}
    x=enrich(d);c=float(x.Close.iloc[-1]);e18=float(x.EMA18.iloc[-1]);e50=float(x.EMA50.iloc[-1]);e200=float(x.EMA200.iloc[-1]);sc=sum([c>e18,e18>e50,e50>e200,c>x.Close.iloc[-10],c>x.Close.iloc[-20]])
    return {'bias':'BULLISH TREND' if sc>=4 else 'BEARISH TREND' if sc<=1 else 'MIXED / RANGE','score':int(sc),'close':c,'ema18':e18,'ema50':e50,'ema200':e200,'rsi':float(x.RSI.iloc[-1]),'atr':float(x.ATR.iloc[-1])}

def liquidity(d):
    if len(d)<20:return 'No clear sweep'
    x=d.tail(31);last=x.iloc[-1];ph=x.High.iloc[:-1].max();pl=x.Low.iloc[:-1].min()
    if last.High>ph and last.Close<ph:return 'BUY-SIDE SWEEP'
    if last.Low<pl and last.Close>pl:return 'SELL-SIDE SWEEP'
    return 'NO CLEAR SWEEP'

def fvg_count(d):
    if len(d)<5:return 0
    x=d.tail(100).reset_index(drop=True);n=0
    for i in range(2,len(x)):
        n += int(x.Low.iloc[i]>x.High.iloc[i-2] or x.High.iloc[i]<x.Low.iloc[i-2])
    return n

def chart(d, height=250):
    if go is None or d.empty:return None
    x=enrich(d).tail(180);fig=go.Figure()
    fig.add_trace(go.Candlestick(x=x.index,open=x.Open,high=x.High,low=x.Low,close=x.Close,name='Price',increasing_line_color='#00ef9b',decreasing_line_color='#ff405b'))
    for col,name,colr in [('EMA18','EMA18','#ffd34e'),('EMA50','EMA50','#13d8ff')]:fig.add_trace(go.Scatter(x=x.index,y=x[col],name=name,line=dict(color=colr,width=1.4)))
    fig.update_layout(height=height,margin=dict(l=4,r=4,t=4,b=4),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#a9bdc9',size=9),xaxis_rangeslider_visible=False,legend=dict(orientation='h',y=1.03),xaxis=dict(gridcolor='#102838'),yaxis=dict(gridcolor='#102838'))
    return fig

def market_tile(name,sym):
    d=fetch(sym,'5d','1d')
    if d.empty:return f'<div class="ticker"><div class="name">{name}</div><div class="px">—</div><div class="small">Data unavailable</div></div>'
    last=float(d.Close.iloc[-1]);prev=float(d.Close.iloc[-2]) if len(d)>1 else last;chg=(last/prev-1)*100 if prev else 0;cl='up' if chg>=0 else 'down';arrow='▲' if chg>=0 else '▼'
    return f'<div class="ticker"><div class="name">{name}</div><div class="px">{last:,.2f}</div><div class="{cl}">{arrow} {chg:+.2f}%</div></div>'

def ai_chart(files,symbol,model):
    key=os.getenv('OPENAI_API_KEY','')
    if not key:
        try:key=st.secrets.get('OPENAI_API_KEY','')
        except Exception:key=''
    if not key:return 'OPENAI_API_KEY is not configured in Streamlit Secrets.'
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        content=[{'type':'input_text','text':f'''You are VS FLOW AI Chart Analyzer. Analyze only visible evidence. Symbol: {symbol or 'unknown'}. Use MTF 1W→1D→4H→1H→30M→15M→5M→1M. Higher TF decides LOCATION; lower TF decides TRIGGER. Core: LOCATION→LIQUIDITY→TRIGGER→ENTRY. Evaluate supply/demand, OB, FVG/iFVG, AMD, premium/discount, liquidity sweeps, BOS/CHoCH, trendline, 18-day MA, correction quality, volatility, risk. Output a concise VFTC: overview, MTF table, bias, regime, location, trigger, entry zone, SL/invalidation, TP1/TP2/TP3, R:R, score/100, status BUY/SELL/EARLY/WAIT/NO TRADE. Never invent unreadable prices and never guarantee profit.''' }]
        for f in files:
            b64=base64.b64encode(f['bytes']).decode();content.append({'type':'input_image','image_url':f"data:{f.get('mime','image/png')};base64,{b64}"})
        r=client.responses.create(model=model,input=[{'role':'user','content':content}],max_output_tokens=4500)
        return r.output_text
    except Exception as e:return f'AI analysis error: {e}'

# Sidebar
with st.sidebar:
    if LOGO.exists():st.image(str(LOGO),use_container_width=True)
    st.markdown('### ⚡ VS FLOW AI MASTER')
    pages=['🏠 Dashboard','🔎 Universal Search','🤖 AI Chart Analyzer','🔥 VS FLOW Core','⚡ VS FLOW Early','🧬 AMD + iFVG','🏆 World-Class Strategy','📡 Master Scanner','📊 Options & OI','🧪 Quant / Backtest','🎯 VFTC','📓 Trading Journal','⚙️ Settings']
    page=st.radio('NAVIGATION',pages,index=0,key='page')
    st.divider();st.markdown('**MTF ENGINE**');st.caption('1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M');st.caption('LOCATION → LIQUIDITY → TRIGGER → ENTRY')
    st.markdown('<div class="small">WAIT is a valid result • Research / educational use</div>',unsafe_allow_html=True)

# Header
logo_b64=''
if LOGO.exists():logo_b64=base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(f'''<div class="hero"><div class="hero-row"><div class="hero-left"><img class="hero-logo" src="data:image/png;base64,{logo_b64}"><div><div class="brand">VS FLOW</div><div class="sub">ALL MARKETS • ONE VISION • TRADE SMARTER • LIVE BETTER</div></div></div><div class="owner"><b>VAIBHAV SHIRSAT</b><span>TRADER • ANALYZER • BUILDER</span></div></div></div>''',unsafe_allow_html=True)

# Universal search
c1,c2,c3=st.columns([6,1.2,1.0])
q=c1.text_input('search','',placeholder='Search any symbol… RELIANCE, NIFTY, BTC, GOLD, AAPL, EURUSD, CRUDE',label_visibility='collapsed')
market=c2.selectbox('market',['Auto','India','Global','Crypto','Commodity'],label_visibility='collapsed')
if c3.button('📈 ANALYZE',use_container_width=True) and q:
    st.session_state['asset_query']=q;st.session_state['asset_market']=market;st.session_state['asset']=resolve(q,market)

# Dashboard
if page=='🏠 Dashboard':
    tiles=st.columns(8)
    tile_data=[('🇮🇳 NIFTY 50','^NSEI'),('🇮🇳 BANKNIFTY','^NSEBANK'),('🇮🇳 INDIA VIX','^INDIAVIX'),('🇺🇸 S&P 500','^GSPC'),('🇺🇸 NASDAQ','^IXIC'),('₿ BTC','BTC-USD'),('🪙 GOLD','GC=F'),('🛢️ CRUDE','CL=F')]
    for c,(n,s) in zip(tiles,tile_data):c.markdown(market_tile(n,s),unsafe_allow_html=True)
    st.markdown('<div class="section-title">GLOBAL MARKETS • INDIAN MARKETS • CRYPTO • COMMODITIES • FOREX</div>',unsafe_allow_html=True)
    left,right=st.columns([2.1,1])
    with left:
        st.markdown(f'''<div class="hero-market"><img src="data:image/png;base64,{logo_b64}"><h2>ONE SEARCH • COMPLETE ANALYSIS</h2><p>FROM IDEA TO EXECUTION — EVERYTHING IN ONE PLATFORM</p><div class="goldline">ANALYZE • SCAN • VALIDATE • EXECUTE WITH DISCIPLINE</div></div>''',unsafe_allow_html=True)
        icons=[('🔍','ANALYZE','8 TIMEFRAMES'),('⚡','VS FLOW','CORE SETUP'),('🚀','EARLY','EARLY SETUP'),('🧬','AMD + iFVG','DETECTION'),('🏆','WORLD-CLASS','STRATEGIES'),('📊','OPTIONS','OI + CONTEXT'),('🛡️','RISK','MANAGEMENT'),('🧪','QUANT','BACKTEST'),('🎯','VFTC','TRADE PLAN')]
        st.markdown('<div class="icon-grid">'+''.join([f'<div class="icon-item"><div class="i">{i}</div><b>{b}</b><span>{s}</span></div>' for i,b,s in icons])+'</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel regime"><b>📈 MARKET REGIME</b>',unsafe_allow_html=True)
        reg_q='NIFTY';sym=POPULAR[reg_q];d=fetch(sym,'6mo','1d');s=structure(d)
        color='green' if 'BULL' in s['bias'] else 'red' if 'BEAR' in s['bias'] else 'gold'
        st.markdown(f'<div class="regime-big {color}">↗ {s["bias"]}</div>',unsafe_allow_html=True)
        for b in ['Higher Highs / Higher Lows' if 'BULL' in s['bias'] else 'Lower Highs / Lower Lows' if 'BEAR' in s['bias'] else 'Mixed structure','Price vs key EMAs','Momentum / RSI context','Liquidity + institutional location']:
            st.markdown(f'<div class="bullet">• {b}</div>',unsafe_allow_html=True)
        if not d.empty:
            fig=chart(d,190)
            if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">TODAY’S BEST SETUPS</div>',unsafe_allow_html=True)
    setup_symbols=['RELIANCE.NS','HDFCBANK.NS','NIFTY','BTC-USD','GC=F']
    rows=[]
    for sym in setup_symbols:
        d=fetch(resolve(sym,'Auto'),'1mo','1d');s=structure(d)
        if d.empty:continue
        direction='BUY' if 'BULL' in s['bias'] else 'SELL' if 'BEAR' in s['bias'] else 'WAIT';score=min(99,60+s['score']*7+int(max(0,min(10,abs(s['rsi']-50)/3))))
        rows.append((sym.replace('.NS',''), '1D', 'Core Setup' if direction!='WAIT' else 'Monitor', direction, score))
    html='<div class="panel"><div class="setup-row head"><div>SYMBOL</div><div>TIMEFRAME</div><div>SETUP TYPE</div><div>DIRECTION</div><div>SCORE</div></div>'
    for a,b,c,dv,e in rows:html+=f'<div class="setup-row"><div>{a}</div><div>{b}</div><div>{c}</div><div><span class="badge {"buy" if dv=="BUY" else "sell"}">{"▲" if dv=="BUY" else "▼" if dv=="SELL" else "•"} {dv}</span></div><div><span class="score">{e}</span></div></div>'
    html+='</div>';st.markdown(html,unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="panel"><b>📊 SECTOR PULSE</b><div class="bullet">Banking <span class="green">+0.82%</span></div><div class="bullet">IT <span class="green">+0.45%</span></div><div class="bullet">Financial Services <span class="green">+0.38%</span></div><div class="bullet">FMCG <span class="red">-0.21%</span></div><div class="bullet">Pharma <span class="red">-0.35%</span></div></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><b>🌐 MARKET BREADTH</b><div style="text-align:center;font-size:42px;font-weight:1000;color:#00ef9b;margin:15px">62%</div><div class="small" style="text-align:center">ADVANCE / DECLINE CONTEXT</div></div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="panel"><b>🛡️ TRADE GUARD</b><div class="bullet">Risk Control <span class="green">GOOD</span></div><div class="bullet">Volatility <span class="gold">MODERATE</span></div><div class="bullet">News Risk <span class="green">LOW</span></div><div class="bullet">FOMO Risk <span class="red">HIGH</span></div><div style="margin-top:15px;padding:8px;text-align:center;border:1px solid #00b978;color:#00ef9b;border-radius:8px;font-weight:900">TRADE READY = ONLY AFTER VFTC CONFIRMATION</div></div>',unsafe_allow_html=True)

elif page=='🔎 Universal Search':
    st.markdown('<div class="section-title">UNIVERSAL SEARCH • COMPLETE BREAKDOWN</div>',unsafe_allow_html=True)
    q2=st.session_state.get('asset_query',q)
    if not q2:st.info('Search a symbol above to begin.');st.stop()
    sym=st.session_state.get('asset',resolve(q2,market));d=fetch(sym,'1y','1d');s=structure(d)
    if d.empty:st.error('No market data returned. Try a supported symbol.');st.stop()
    m=st.columns(6)
    for c,k,v in zip(m,['SYMBOL','BIAS','SCORE','RSI','EMA18','ATR'],[sym,s['bias'],f"{s['score']}/5",f"{s['rsi']:.1f}",f"{s['ema18']:.2f}",f"{s['atr']:.2f}"]):c.markdown(f'<div class="metric-card"><div class="k">{k}</div><div class="v">{v}</div></div>',unsafe_allow_html=True)
    fig=chart(d,390)
    if fig:st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    rows=[('HTF Trend',s['bias'],'Context'),('18-Day MA','Aligned' if (s['close']>s['ema18']) else 'Below','Trend filter'),('Liquidity',liquidity(d),'Liquidity'),('FVG',f'{fvg_count(d)} detected','Location / trigger'),('OB','Visual confirmation required','Institutional zone'),('AMD','Visual confirmation required','Accumulation → manipulation → distribution'),('iFVG','Visual confirmation required','Inverse FVG'),('VFTC','Generate after MTF confirmation','Final decision card')]
    st.dataframe(pd.DataFrame(rows,columns=['MODULE','RESULT','ROLE']),use_container_width=True,hide_index=True)

elif page=='🤖 AI Chart Analyzer':
    st.markdown('<div class="section-title">AI CHART ANALYZER • PASTE → ANALYZE → VFTC</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel" style="text-align:center;padding:24px"><div style="font-size:24px">📋 PASTE CHART HERE</div><div class="small">Upload 1W → 1D → 4H → 1H → 30M → 15M → 5M → 1M for complete MTF analysis.</div></div>',unsafe_allow_html=True)
    uploads=st.file_uploader('Chart screenshots',type=['png','jpg','jpeg','webp'],accept_multiple_files=True)
    labels=['1W','1D','4H','1H','30M','15M','5M','1M'];files=[]
    if uploads:
        for i,f in enumerate(uploads):
            tf=st.selectbox(f.name,labels,index=min(i,7),key=f'ai_tf_{i}');files.append({'timeframe':tf,'bytes':f.getvalue(),'mime':f.type})
    symbol=st.text_input('Symbol / instrument','',key='ai_symbol');model=st.selectbox('AI Model',['gpt-5.6-luna','gpt-5.6-sol'])
    if st.button('⚡ RUN AI VFTC ANALYSIS',type='primary',use_container_width=True):
        if not files:st.warning('Upload at least one chart screenshot.')
        else:
            with st.spinner('Running VS FLOW MTF + AI analysis…'):st.session_state['ai_result']=ai_chart(files,symbol,model)
    if st.session_state.get('ai_result'):st.markdown('<div class="panel">'+st.session_state['ai_result'].replace('\n','<br>')+'</div>',unsafe_allow_html=True)

elif page in ['🔥 VS FLOW Core','⚡ VS FLOW Early','🧬 AMD + iFVG','🏆 World-Class Strategy','📡 Master Scanner','📊 Options & OI','🧪 Quant / Backtest','🎯 VFTC','📓 Trading Journal','⚙️ Settings']:
    titles={'🔥 VS FLOW Core':'VS FLOW CORE SETUP','⚡ VS FLOW Early':'VS FLOW EARLY SETUP','🧬 AMD + iFVG':'AMD + iFVG ENGINE','🏆 World-Class Strategy':'WORLD-CLASS STRATEGY LAB','📡 Master Scanner':'MASTER SCANNER','📊 Options & OI':'OPTIONS & OI CONTEXT','🧪 Quant / Backtest':'QUANT / BACKTEST LAB','🎯 VFTC':'VS FLOW TRADE CARD (VFTC)','📓 Trading Journal':'TRADING JOURNAL','⚙️ Settings':'SETTINGS'}
    st.markdown(f'<div class="section-title">{titles[page]}</div>',unsafe_allow_html=True)
    if page=='🔥 VS FLOW Core':
        st.markdown('<div class="panel"><b class="gold">CORE LOGIC</b><br><br><b>LOCATION → LIQUIDITY → TRIGGER → ENTRY</b><br><span class="small">Higher timeframe decides WHERE. Lower timeframe decides WHEN. Scanner candidates never override manual MTF confirmation.</span></div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([['1W','Macro context',15],['1D','Primary structure',20],['4H','Main location',20],['1H','Liquidity / structure',15],['30M','Correction development',10],['15M','Trigger preparation',8],['5M','Entry confirmation',10],['1M','Precision only',2]],columns=['TF','ROLE','WEIGHT']),use_container_width=True,hide_index=True)
    elif page=='⚡ VS FLOW Early':
        cols=st.columns(4)
        for c,k,v in zip(cols,['COMPRESSION','LIQUIDITY','FRESH OB','TRIGGER'],['DEVELOPING','NEARBY','SCAN / VERIFY','PENDING']):c.markdown(f'<div class="metric-card"><div class="k">{k}</div><div class="v gold">{v}</div></div>',unsafe_allow_html=True)
        st.info('Early = developing setup. It becomes a trade only after Core confirmation.')
    elif page=='🧬 AMD + iFVG':
        st.code('ACCUMULATION → LIQUIDITY BUILD → MANIPULATION / SWEEP → DISPLACEMENT → iFVG → DISTRIBUTION')
        st.dataframe(pd.DataFrame([['Accumulation','Range / inventory'],['Manipulation','Liquidity sweep / false break'],['Distribution','Displacement / expansion'],['iFVG','FVG invalidation → inverse retest']],columns=['MODULE','READ']),use_container_width=True,hide_index=True)
    elif page=='🏆 World-Class Strategy':
        st.dataframe(pd.DataFrame([['Pau Perdices Bellet','Trend → correction → key level → reversal + risk'],['Inna Rosputnia','18-day MA trend following + systematic discipline'],['Paul Tudor Jones','Capital preservation + asymmetric R:R'],['Richard Dennis','Breakout + ATR risk'],['Jim Simons','Quant validation / systematic testing'],['Darvas','Box breakout'],['Livermore','Trend + winner management'],['Suricate Trading','COT + term structure + volume profile']],columns=['FRAMEWORK','INTEGRATION']),use_container_width=True,hide_index=True)
    elif page=='📡 Master Scanner':
        raw=st.text_area('Symbols (one per line or comma separated)','RELIANCE\nTCS\nHDFCBANK\nICICIBANK\nNIFTY\nBTC\nGOLD')
        if st.button('🚀 RUN MASTER SCAN',use_container_width=True):
            out=[]
            for item in re.split(r'[\n,; ]+',raw):
                if not item:continue
                d=fetch(resolve(item),'1mo','1d');s=structure(d)
                if d.empty:continue
                direction='BUY' if 'BULL' in s['bias'] else 'SELL' if 'BEAR' in s['bias'] else 'WAIT';score=60+s['score']*7
                out.append([item,direction,round(s['rsi'],1),liquidity(d),fvg_count(d),min(score,99)])
            st.dataframe(pd.DataFrame(out,columns=['SYMBOL','DIRECTION','RSI','LIQUIDITY','FVG','SCORE']),use_container_width=True,hide_index=True)
    elif page=='📊 Options & OI':
        st.info('Options/OI is a context layer. Price structure remains primary. Broker/NSE live chain integration can be connected separately.')
        cols=st.columns(5)
        for c,k in zip(cols,['PCR','IV','INDIA VIX','MAX PAIN','OI WALLS']):c.markdown(f'<div class="metric-card"><div class="k">{k}</div><div class="v">—</div><div class="small">Context feed</div></div>',unsafe_allow_html=True)
    elif page=='🧪 Quant / Backtest':
        st.code('HYPOTHESIS → BACKTEST → OUT-OF-SAMPLE → WALK-FORWARD → PAPER TRADE → PRODUCTION')
        st.dataframe(pd.DataFrame([['Expectancy','Average R per trade'],['Profit Factor','Gross profit / gross loss'],['Max Drawdown','Capital risk'],['MAE / MFE','Trade quality'],['Consecutive Losses','Risk resilience']],columns=['METRIC','PURPOSE']),use_container_width=True,hide_index=True)
    elif page=='🎯 VFTC':
        a,b,c=st.columns(3);sym=a.text_input('Symbol','NIFTY');bias=b.selectbox('Bias',['BUY','SELL','WAIT']);reg=c.selectbox('Regime',['Strong Trend','Range','Expansion','Unclear'])
        vals={};weights={'HTF Trend':15,'Market Regime':10,'HTF Location':15,'18-Day MA':5,'Correction Quality':10,'Liquidity':10,'CHoCH/BOS':10,'FVG/Displacement':5,'Volume/Profile':5,'R:R':10}
        left,right=st.columns(2)
        for i,(k,w) in enumerate(weights.items()):vals[k]= (left if i%2==0 else right).slider(k,0,w,max(0,w//2),key='v4_'+k)
        total=sum(vals.values());status='VALID A+ CANDIDATE' if total>=85 else 'VALID A CANDIDATE' if total>=75 else 'WAIT / MONITOR' if total>=65 else 'NO TRADE'
        if vals['HTF Location']==0:status='NO TRADE — NO VALID LOCATION'
        m=st.columns(3);m[0].metric('VFTC SCORE',f'{total}/100');m[1].metric('BIAS',bias);m[2].metric('STATUS',status)
        st.markdown(f'<div class="panel"><b class="gold">{sym} • VFTC FINAL RESULT</b><br><br>1. Analysis Overview<br>2. Bias: <b>{bias}</b><br>3. Confidence: {total}/100<br>4. Entry Zone: define only after location + trigger<br>5. Stop Loss: logical invalidation<br>6. TP1 / TP2 / TP3: structure-based<br>7. Risk:Reward: require acceptable asymmetry<br>8. Market Context: {reg}<br>9. Multi-Timeframe Analysis: 1W→1D→4H→1H→30M→15M→5M→1M<br>10. Setup Status: <b>{status}</b><br>11. Invalidation: thesis invalidation level<br>12. Final Result: <b>{status}</b></div>',unsafe_allow_html=True)
    elif page=='📓 Trading Journal':
        st.info('Journal module ready for CSV persistence. Keep entries factual: setup, risk, execution, result, lesson.')
        st.dataframe(pd.DataFrame(columns=['Date','Symbol','Setup','Bias','Risk','Result','Lesson']),use_container_width=True,hide_index=True)
    elif page=='⚙️ Settings':
        st.write(f'**Version:** {VERSION}');st.write(f'**Owner:** {AUTHOR}');st.code('OPENAI_API_KEY = "sk-..."',language='toml');st.warning('Never commit API keys to GitHub. Add them only in Streamlit Secrets.')

st.markdown(f'<div style="margin-top:20px;border-top:1px solid #17374c;padding:9px;color:#688093;font-size:9px">{APP} {VERSION} • {AUTHOR} • ALL MARKETS • ONE VISION • Educational / research use only</div>',unsafe_allow_html=True)
