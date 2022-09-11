from app import app
from flask import request, jsonify
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

@app.route('/detik', methods=["POST"])
def test():
	keyword = request.json['keyword']

	user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
	headers = {'User-Agent': user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

	news = []

	for page in range(1,5):
		url = 'https://www.detik.com/search/searchall?query={}&sortby=time&page='.format(keyword) + str(page)
		req = Request(url, headers=headers)
		html = urlopen(req)

		data = bs(html, 'html.parser')
		box = data.find_all('article')

		for each in box:
			new_url = each.a.get('href')
			
			if 'travel.detik.com' not in new_url:
				new_req = Request(new_url, headers=headers)
				new_html = urlopen(new_req)

				new_data = bs(new_html, 'html.parser')            
				new_box = new_data.find('div',{'class', 'detail__body-text itp_bodycontent'})

				hidelabel = new_box.find_all('table',{"class","linksisip"})
				for delete in hidelabel:
					delete.decompose()

				items = new_box.find_all('p')
				hasil = [item.get_text() for item in items]

				hasil = [item.lower() for item in hasil]
				hasil = [' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", item).split()) for item in hasil]
				paragraf = ' '.join(hasil)
				stop_words = set(stopwords.words('indonesian'))
				word_tokens = word_tokenize(paragraf) 
				paragraf_2 = ' '.join([w for w in word_tokens if not w in stop_words])
				
				
				if new_data.find('div',{'class','detail__media'}).img is not None:
					url_gambar = new_data.find('div',{'class','detail__media'}).img.get('src')
					judul = re.sub('\n','',new_data.find('h1',{'class', 'detail__title'}).text).strip()
					penulis = new_data.find('div',{'class', 'detail__author'}).text
					tanggal = new_data.find('div',{'class', 'detail__date'}).text

					news.append({'title':judul, 'date':tanggal, 'author':penulis, 'content':paragraf_2, 'image_url':url_gambar})

	resp = jsonify(news)
	return resp
		
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp
		
if __name__ == "__main__":
    app.run(debug=True)