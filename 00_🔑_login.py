"""login page"""  # noqa: N999

from datetime import date, datetime
from typing import Any

import streamlit as st
import streamlit_authenticator as stauth
from loguru import logger
from streamlit_lottie import st_lottie

import modules.logger_setup
from modules import constants as cont
from modules import setup_stuff
from modules import streamlit_menus as sm
from modules import user_authentication as uauth
from modules.general_functions import func_timer, load_lottie_file
from modules.logger_setup import LogLevel

st.set_page_config(
    page_title="UTEC Online Tools",
    page_icon="logo/UTEC_logo.png",
    layout="wide",
)

# general page config (Favicon, etc.)
if not st.session_state.get("logger_setup"):
    modules.logger_setup.logger_setup()

if st.session_state.get("initial_setup"):
    logger.log(LogLevel.NEW_RUN.name, "NEW RUN")
else:
    setup_stuff.general_setup()

setup_stuff.page_header_setup(page="login")


@func_timer
def display_login_page() -> None:
    """Login-Page with two columns
    - login with username and password
    - lottie-animation
    """
    columns: list = st.columns(2)

    with columns[0]:
        login_section()
    with columns[1]:
        st_lottie(
            load_lottie_file("animations/login.json"), height=450, key="lottie_login"
        )


@func_timer
def login_section() -> None:
    """User authentication part of the login page"""

    user_credentials: dict[str, dict[str, Any]] = uauth.format_user_credentials()
    authenticator: stauth.Authenticate = stauth.Authenticate(
        credentials=user_credentials,
        cookie_name="utec_tools",
        key="uauth",
        cookie_expiry_days=30,
    )

    authenticator.login("Login", "main")

    if st.session_state["authentication_status"]:
        access_granted()

        st.markdown("---")
        authenticator.logout("Logout", "main")

    elif st.session_state["authentication_status"] is None:
        st.warning("Bitte Benutzernamen und Passwort eingeben")
    else:
        st.error("Benutzername oder Passwort falsch")
        logger.error("Benutzername oder Passwort falsch")


@func_timer
def access_granted() -> None:
    """If access is granted, do this..."""

    # determine the access level
    user_key: str = st.session_state["username"]
    all_users: dict[str, dict[str, Any]] = st.session_state["all_user_data"]
    access_lvl_user: str | list = all_users[user_key]["access_lvl"]
    st.session_state["access_lvl"] = access_lvl_user

    # log used username and access level
    if st.session_state.get("logged_username") != user_key:
        logger.success(f"logged in as: {user_key}, access level: {access_lvl_user}")
        st.session_state["logged_username"] = user_key

    if access_lvl_user in ("god", "full"):
        st.session_state["access_pages"] = list(cont.PAGES)
        st.session_state["access_until"] = date.max
    else:
        st.session_state["access_pages"] = access_lvl_user
        st.session_state["access_until"] = (
            datetime.strptime(all_users[user_key]["access_until"], "%Y-%m-%d")
            .astimezone()
            .date()
        )

    if st.session_state.get("username") in ["utec"]:
        st.markdown(uauth.MessageLog.access_utec.message)

    else:
        st.markdown(uauth.MessageLog.access_other.message)

        if st.session_state["access_until"] < date.max:
            st.markdown(uauth.MessageLog.access_until.message)
        else:
            st.markdown(uauth.MessageLog.access_level.message)

        for page in st.session_state["access_pages"]:
            if page != "login":
                st.markdown(f"- {cont.PAGES[page]['page_tit']}")

    if access_lvl_user == "god":
        god_mode()


@func_timer
def god_mode() -> None:
    """Define special stuff for users with access level 'god'"""

    sm.user_accounts()
    # neuen Benutzer eintragen
    if st.session_state.get("butt_sub_new_user"):
        with st.spinner("Momentle bitte, Benutzer wird hinzugefügt..."):
            uauth.insert_new_user(
                username=st.session_state["new_user_user"],
                name=st.session_state["new_user_name"],
                email=st.session_state["new_user_email"],
                password=st.session_state["new_user_pw"],
                access_lvl=st.session_state["new_user_access"],
                access_until=str(st.session_state["new_user_until"]),
            )

    # Benutzer löschen
    if st.session_state.get("butt_sub_del_user"):
        uauth.delete_user()


display_login_page()

logger.success("Login Page Loaded")
