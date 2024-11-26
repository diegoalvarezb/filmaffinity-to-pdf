import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

class FilmaffinityExporter:
    """
    FilmAffinity Exporter
    """

    def __init__(self, user_id):
        """
        Initialize a FilmaffinityExporter instance.
        """
        self.user_id = user_id
        self.base_url = f"https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&chv=list&orderby=rating"
        self.movies = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }

    def _extract_movie_data(self, movie, parent_element):
        """
        Extract all movie data from HTML elements.
        """
        title_elem = movie.find('div', class_='mc-title').find('a', class_='d-md-inline-block')
        year_elem = movie.find('span', class_='mc-year')
        rating_elem = movie.find('div', class_='fa-avg-rat-box').find('div', class_='avg')
        own_rating_elem = parent_element.find('div', class_='fa-user-rat-box')
        director_elem = movie.find('div', class_='mc-director')
        cast_elem = movie.find('div', class_='mc-cast')
        poster_img = movie.find('img', class_='lazyload')
        flag_img = movie.find('img', class_='nflag')

        return {
            'title': title_elem.text.strip() if title_elem else "Unknown",
            'year': year_elem.text.strip() if year_elem else "",
            'rating': rating_elem.text.strip() if rating_elem else "",
            'own_rating': own_rating_elem.text.strip() if own_rating_elem else "",
            'director': director_elem.text.strip() if director_elem else "",
            'cast': cast_elem.text.strip() if cast_elem else "",
            'poster_url': poster_img.get('data-srcset', '').split(' ')[0] if poster_img else "",
            'flag_url': 'https://www.filmaffinity.com/' + flag_img.get('src', '') if flag_img else ""
        }

    def _create_styles(self):
        """
        Create and return all necessary styles for the PDF.
        """
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1F497D'),
            fontName='Helvetica-Bold'
        )

        movie_title_style = ParagraphStyle(
            'MovieTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E74B5'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        )

        rating_style = ParagraphStyle(
            'RatingStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#C00000'),
            fontName='Helvetica',
            spaceAfter=4
        )

        general_rating_style = ParagraphStyle(
            'GeneralRatingStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#C00000'),
            fontName='Helvetica',
            spaceAfter=4
        )

        movie_info_style = ParagraphStyle(
            'MovieInfo',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica',
        )

        return {
            'title': title_style,
            'movie_title': movie_title_style,
            'rating': rating_style,
            'general_rating': general_rating_style,
            'movie_info': movie_info_style
        }

    def _create_movie_poster_cell(self, movie):
        """
        Create and return the poster cell for a movie.
        """
        poster_cell = []

        if movie.get('poster_url'):
            try:
                img_data = requests.get(movie['poster_url'], headers=self.headers).content
                img = Image(BytesIO(img_data))
                img.drawHeight = 1.2*inch
                img.drawWidth = 0.8*inch
                poster_cell.append(img)
            except Exception as e:
                print(f"Error loading poster for {movie['title']}: {e}")

        return poster_cell

    def _create_movie_title_table(self, movie, styles):
        """
        Create and return the title table with flag for a movie.
        """
        table_data = [[]]

        # Title
        title_text = f"{movie['title']}"
        title = Paragraph(title_text, styles['movie_title'])
        table_data[0].append(title)

        # Flag
        if movie.get('flag_url'):
            try:
                flag_data = requests.get(movie['flag_url'], headers=self.headers).content
                flag_img = Image(BytesIO(flag_data))
                flag_img.drawHeight = 12
                flag_img.drawWidth = 16
                table_data[0].append(flag_img)
            except Exception as e:
                print(f"Error loading flag for {movie['title']}: {e}")
        else:
            table_data[0].append('')

        # Adjust the widths to match the width of the information column
        title_table = Table(table_data, colWidths=[5.2*inch, 0.3*inch])
        title_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        return title_table

    def _create_movie_info_cell(self, movie, styles, title_table):
        """
        Create and return the info cell for a movie.
        """
        info_cell = []
        info_cell.append(title_table)

        rating_text = f"<b>{movie['own_rating']}</b> ({movie['rating']})"
        ratings = Paragraph(rating_text, styles['rating'])
        info_cell.append(ratings)
        info_cell.append(Spacer(1, 4))

        if movie['year']:
            year = Paragraph(f"<b>Year:</b> {movie['year']}", styles['movie_info'])
            info_cell.append(year)

        if movie['director']:
            director = Paragraph(f"<b>Director:</b> {movie['director']}", styles['movie_info'])
            info_cell.append(director)

        if movie['cast']:
            cast = Paragraph(f"<b>Cast:</b> {movie['cast']}", styles['movie_info'])
            info_cell.append(cast)

        return info_cell

    def _create_movie_separator(self):
        """
        Create and return a separator line between movies.
        """
        line = Table([['']], colWidths=[6.5*inch], rowHeights=[1])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#CCCCCC')),
            ('TOPPADDING', (0,0), (-1,0), 15),
            ('BOTTOMPADDING', (0,0), (-1,0), 15),
        ]))
        return line

    def get_voted_movies(self):
        """
        Retrieves all voted movies from the user's Filmaffinity profile.

        This method scrapes the user's ratings page and extracts information for each movie including:
        - Title
        - Year
        - Overall rating
        - User's rating
        - Director
        - Cast
        - Poster URL
        - Country flag URL

        The data is stored in the self.movies list.
        """
        page = 1
        while True:
            url = f"{self.base_url}&p={page}"
            response = requests.get(url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            movies_elements = soup.find_all('div', class_='user-ratings-movie-item')

            if not movies_elements:
                break

            for movie in movies_elements:
                parent_element = movie.parent

                movie_data = self._extract_movie_data(movie, parent_element)
                self.movies.append(movie_data)

            page += 1

    def export_to_pdf(self, output_filename):
        """
        Export the rated movies to a PDF file.
        """
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=72,
            bottomMargin=72
        )
        elements = []
        styles = self._create_styles()

        for movie in self.movies:
            # Main table for each movie
            movie_data = [[]]

            # Poster cell (left column)
            poster_cell = self._create_movie_poster_cell(movie)
            movie_data[0].append(poster_cell)

            # Information cell (right column)
            info_cell = self._create_movie_info_cell(
                movie,
                styles,
                self._create_movie_title_table(movie, styles)
            )
            movie_data[0].append(info_cell)

            # Create table with poster and information
            movie_table = Table(movie_data, colWidths=[1*inch, 5.5*inch])
            movie_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))

            elements.append(movie_table)
            elements.append(self._create_movie_separator())

        doc.build(elements)

def main():
    """
    Main function
    """
    user_id = input("Please enter your FilmAffinity user ID: ")
    exporter = FilmaffinityExporter(user_id)

    print("Getting rated movies...")
    exporter.get_voted_movies()

    output_filename = f"fa_ratings_{user_id}.pdf"
    print(f"Exporting to PDF: {output_filename}")
    exporter.export_to_pdf(output_filename)

    print(f"Export completed! {len(exporter.movies)} movies have been exported.")

# Run the script only if it's the main module
if __name__ == "__main__":
    main()
