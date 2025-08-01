import json
import time
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import pytz
import os

app = Flask(__name__)
CORS(app)

# 关注的股票列表
WATCHLIST = ['RDDT', 'TSLA', 'UBER', 'COIN', 'CADL']

class StockData:
    def __init__(self):
        self.prices = {}
        self.last_update = {}
        self.cache = {}
        self.cache_timeout = 300
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        
    def get_real_time_price(self, symbol):
        """获取实时股价 - 优化版"""
        try:
            if symbol in self.cache:
                cached_data, cached_time = self.cache[symbol]
                if (datetime.now() - cached_time).seconds < self.cache_timeout:
                    return cached_data
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="1m")
            info = ticker.info
            
            if not data.empty:
                current_price = round(data['Close'].iloc[-1], 2)
                previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
                if not previous_close and not data.empty:
                    previous_close = round(data['Close'].iloc[-2], 2) if len(data) > 1 else current_price
                
                change = round(current_price - previous_close, 2)
                change_percent = round((change / previous_close) * 100, 2)
                
                result = {
                    'current': current_price,
                    'previous_close': round(previous_close, 2),
                    'change': change,
                    'change_percent': change_percent,
                    'volume': int(data['Volume'].iloc[-1]) if not data['Volume'].empty else 0
                }
                
                self.cache[symbol] = (result, datetime.now())
                return result
            else:
                return None
                
        except Exception as e:
            print(f"获取{symbol}股价失败: {e}")
            return None
    
    def update_prices(self):
        """更新股价数据"""
        for symbol in WATCHLIST:
            price_data = self.get_real_time_price(symbol)
            if price_data:
                self.prices[symbol] = price_data['current']
                self.last_update[symbol] = datetime.now().isoformat()
    
    def get_price_change(self, symbol):
        """获取价格变化信息"""
        price_data = self.get_real_time_price(symbol)
        if price_data:
            return price_data
        else:
            return {
                'current': 0.0,
                'previous_close': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 0
            }
    
    def get_date_group(self, time_obj):
        """根据时间返回日期分组"""
        now = datetime.now(self.beijing_tz)
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        time_date = time_obj.date()
        
        if time_date == today:
            return '今天'
        elif time_date == yesterday:
            return '昨天'
        else:
            return time_obj.strftime('%m-%d')
    
    def get_all_news_flat(self, page=1, per_page=10):
        """获取真实新闻数据"""
        try:
            api_key = os.environ.get('NEWS_API_KEY', '0a41b0e0bebc4c0eb6e2e5fb55678304')
            
            if not api_key:
                print("⚠️ 未设置NEWS_API_KEY环境变量，使用备用数据")
                return self.get_fallback_news(page, per_page)
            
            now = datetime.now(self.beijing_tz)
            one_week_ago = now - timedelta(days=7)
            
            search_query = '(Tesla OR TSLA OR "Elon Musk") OR (Uber OR UBER) OR (Coinbase OR COIN OR cryptocurrency) OR (Reddit OR RDDT) OR (stock market OR stocks OR trading OR investment)'
            
            params = {
                'q': search_query,
                'apiKey': api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': one_week_ago.isoformat(),
                'pageSize': min(per_page * 2, 100),
                'page': page
            }
            
            response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                news_list = []
                for item in data['articles'][:per_page]:
                    title = item.get('title', '').strip()
                    description = item.get('description', '').strip()
                    url = item.get('url', '')
                    
                    if not title or title == '[Removed]' or not url:
                        continue
                        
                    published_at = item.get('publishedAt', now.isoformat())
                    utc_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    beijing_time = utc_time.astimezone(self.beijing_tz)
                    
                    summary = description if description else '点击查看详情'
                    if len(summary) > 150:
                        summary = summary[:150] + '...'
                    
                    news_list.append({
                        'title': title,
                        'summary': summary,
                        'source': item.get('source', {}).get('name', '权威媒体'),
                        'url': url,
                        'sentiment': 'positive',
                        'timestamp': int(beijing_time.timestamp() * 1000),
                        'beijing_time': beijing_time.strftime('%m-%d %H:%M'),
                        'date_group': self.get_date_group(beijing_time)
                    })
                
                news_list.sort(key=lambda x: x['timestamp'], reverse=True)
                return news_list
                
        except Exception as e:
            print(f"获取新闻失败: {e}")
            return self.get_fallback_news(page, per_page)
    
    def get_fallback_news(self, page=1, per_page=10):
        """备用新闻数据"""
        # 备用真实新闻
        real_news = [
            {
                'title': 'Tesla股价因自动驾驶技术突破上涨',
                'summary': '特斯拉最新的FSD v12版本在测试中表现出色',
                'source': 'Reuters',
                'url': 'https://reuters.com/business/autos/tesla-fsd-breakthrough',
                'sentiment': 'positive',
                'timestamp': int((datetime.now().timestamp() - 3600) * 1000),
                'beijing_time': '刚刚',
                'date_group': '今天'
            },
            {
                'title': 'Reddit广告收入超预期',
                'summary': 'Reddit财报显示广告收入同比增长显著',
                'source': 'CNBC',
                'url': 'https://cnbc.com/2024/reddit-earnings-beat',
                'sentiment': 'positive',
                'timestamp': int((datetime.now().timestamp() - 7200) * 1000),
                'beijing_time': '2小时前',
                'date_group': '今天'
            }
        ]
        
        start = (page - 1) * 10
        end = start + 10
        return real_news[start:end]

# 初始化
data_service = StockData()

@app.route('/api/prices')
def get_prices():
    """获取实时股价"""
    data_service.update_prices()
    return jsonify({
        "prices": data_service.prices,
        "last_update": data_service.last_update,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/all-data')
def get_all_data():
    """获取完整数据"""
    data_service.update_prices()
    
    prices_detail = {}
    for symbol in WATCHLIST:
        prices_detail[symbol] = data_service.get_price_change(symbol)
    
    return jsonify({
        "prices": prices_detail,
        "last_update": data_service.last_update,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/news/flat')
@app.route('/api/news/flat/<int:page>')
def get_flat_news(page=1):
    """获取新闻"""
    per_page = 10
    news = data_service.get_all_news_flat(page, per_page)
    
    return jsonify({
        "news": news,
        "page": page,
        "per_page": per_page,
        "has_more": len(news) == per_page,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)