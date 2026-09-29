import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock


URL = "https://svc.ptc.gov.ye/4g/"
PHONE = "رقمك"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Referer": URL,
}


class Yemen4GApp(App):

    def build(self):

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        title = Label(
            text="Yemen 4G",
            font_size=28,
            size_hint_y=None,
            height=60
        )

        self.status = Label(
            text="Loading CAPTCHA...",
            font_size=18,
            size_hint_y=None,
            height=45
        )

        self.captcha = KivyImage(
            size_hint_y=None,
            height=130
        )

        self.captcha_input = TextInput(
            hint_text="Enter CAPTCHA",
            multiline=False,
            input_filter="int",
            font_size=22,
            size_hint_y=None,
            height=55
        )

        refresh_button = Button(
            text="Refresh CAPTCHA",
            font_size=18,
            size_hint_y=None,
            height=55
        )

        refresh_button.bind(
            on_press=self.load_captcha
        )

        check_button = Button(
            text="CHECK BALANCE",
            font_size=20,
            size_hint_y=None,
            height=60
        )

        check_button.bind(
            on_press=self.check_balance
        )

        self.result = Label(
            text="",
            font_size=20
        )

        self.root_layout.add_widget(title)
        self.root_layout.add_widget(self.status)
        self.root_layout.add_widget(self.captcha)
        self.root_layout.add_widget(self.captcha_input)
        self.root_layout.add_widget(refresh_button)
        self.root_layout.add_widget(check_button)
        self.root_layout.add_widget(self.result)

        Clock.schedule_once(
            lambda dt: self.load_captcha(),
            0.5
        )

        return self.root_layout


    def load_captcha(self, *args):

        self.status.text = "Loading CAPTCHA..."
        self.result.text = ""

        try:

            response = self.session.get(
                URL,
                timeout=30
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            nonce = soup.find(
                "input",
                {"name": "qb4g_nonce_field"}
            )

            captcha_img = soup.find(
                "img",
                {"id": "qp4g-captcha_img"}
            )

            if not nonce or not captcha_img:

                self.status.text = (
                    "Could not get CAPTCHA"
                )

                return

            self.nonce = nonce.get("value")

            self.captcha_url = captcha_img.get("src")

            captcha_response = self.session.get(
                self.captcha_url,
                headers={
                    "Referer": URL
                },
                timeout=30
            )

            captcha_response.raise_for_status()

            image = Image.open(
                BytesIO(
                    captcha_response.content
                )
            )

            image.save(
                "captcha_gui.png"
            )

            self.captcha.source = (
                "captcha_gui.png"
            )

            self.captcha.reload()

            self.captcha_input.text = ""

            self.status.text = (
                "Enter CAPTCHA"
            )

        except Exception as e:

            self.status.text = (
                f"Error: {e}"
            )


    def check_balance(self, *args):

        captcha_code = (
            self.captcha_input.text.strip()
        )

        if len(captcha_code) != 5:

            self.status.text = (
                "CAPTCHA must be 5 digits"
            )

            return

        self.status.text = (
            "Checking balance..."
        )

        self.result.text = ""

        try:

            data = {

                "qb4g_nonce_field":
                    self.nonce,

                "_wp_http_referer":
                    "/4g/",

                "qb4g_submit":
                    "YES",

                "phone4gidnew":
                    PHONE,

                "captcha_code_q4Gbill":
                    captcha_code,

                "qsubmitnew":
                    "استعلام",
            }

            response = self.session.post(

                URL,

                data=data,

                headers={
                    "Referer": URL
                },

                timeout=30
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            balance = None
            expiry = None

            for row in soup.find_all("tr"):

                th = row.find("th")
                td = row.find("td")

                if not th or not td:
                    continue

                label = th.get_text(
                    " ",
                    strip=True
                )

                value = td.get_text(
                    " ",
                    strip=True
                )

                if (
                    label == "الرصيد المتاح"
                    and "GB" in value
                ):

                    balance = value

                elif (
                    label ==
                    "تاريخ انتهاء الرصيد"
                ):

                    expiry = value

            page_text = soup.get_text(
                " ",
                strip=True
            )

            if balance is None:

                if "رمز التحقق" in page_text:

                    self.status.text = (
                        "Wrong CAPTCHA"
                    )

                else:

                    self.status.text = (
                        "Balance not found"
                    )

                self.load_captcha()

                return

            self.status.text = (
                "Balance loaded successfully"
            )

            self.result.text = (

                f"Balance: {balance}\n"

                f"Expiry: "
                f"{expiry or 'Unknown'}"
            )

            with open(
                "result.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    response.text
                )

        except Exception as e:

            self.status.text = (
                "Connection error"
            )

            self.result.text = str(e)


if __name__ == "__main__":

    Yemen4GApp().run()
