import requests
from bs4 import BeautifulSoup
import time
import random
import re

BASE_URL = "https://immo.mitula.ma"

def clean_text(text):
    """Nettoie du texte en supprimant les espaces superflus."""
    return re.sub(r'\s+', ' ', text.strip()) if text else ""

class MitulaScraper:
    def __init__(self, city="casablanca", pages=1):
        self.city = city.lower().replace(' ', '-')
        self.pages = pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'fr-FR,fr;q=0.9'
        }

    def _get_url(self, page):
        """Construit l’URL de la page de résultats."""
        if page == 0:
            return f"{BASE_URL}/immo/location-{self.city}"
        return f"{BASE_URL}/immo/location-{self.city}?page={page+1}"

    def _fetch(self, url):
        """Télécharge et parse une page HTML."""
        time.sleep(random.uniform(1, 2))
        resp = requests.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')

    def scrape(self):
        """Récupère les annonces et leurs images."""
        results = []
        for p in range(self.pages):
            soup = self._fetch(self._get_url(p))
            cards = soup.select('article.listing.listing-card') or soup.select('article.listing')
            for card in cards[:10]:
                # titre
                t = card.select_one('div.listing-card__title-and-extra-info__title')
                titre = clean_text(t.text) if t else "-"
                # prix
                pr = card.select_one('span.price__actual')
                prix = clean_text(pr.text) if pr else "-"
                # url de détail
                a = card.select_one('a')
                href = a['href'] if a and a.has_attr('href') else ""
                url_annonce = href if href.startswith('http') else f"{BASE_URL}{href}"
                # description sommaire
                d = card.select_one('div.listing-card__description')
                description = clean_text(d.text) if d else ""
                # image de la carte (fallback)
                img = card.select_one('img.listing-card__image__resource')
                fallback_img = img['src'] if img and img.has_attr('src') else None

                # récupération des vraies images dans la page détaillée
                images = []
                try:
                    detail_soup = self._fetch(url_annonce)
                    for img_tag in detail_soup.select('section.adform .photos img'):
                        src = img_tag.get('data-src') or img_tag.get('src')
                        if src and src not in images:
                            images.append(src)
                except Exception:
                    pass

                image_principale = images[0] if images else fallback_img

                results.append({
                    'titre': titre,
                    'prix': prix,
                    'description': description,
                    'url_annonce': url_annonce,
                    'images': images,
                    'image_principale': image_principale,
                })
        return results
