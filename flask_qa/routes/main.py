import requests
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required

from flask_qa.extensions import db
from flask_qa.models import Stocks, User


main = Blueprint("main", __name__)


def lookup(symbol):
    try:
        api_key = "pk_fa13b2b328ff43bb9a268b23e4c28eba"

        response = requests.get(
            f"https://cloud-sse.iexapis.com/stable/stock/{(symbol)}/quote?token={api_key}"
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        quote = response.json()

    except (KeyError, TypeError, ValueError):
        return None

    return {
        "name": quote["companyName"],
        "price": float(quote["latestPrice"]),
        "symbol": quote["symbol"],
    }


@main.route("/")
@login_required
def index():
    userStocks = (
        db.session.query(
            Stocks.share,
            Stocks.shares,
            Stocks.price
        )
        # .group_by(Stocks.share)
        .filter(Stocks.name == current_user.name)
        .order_by(Stocks.share)
        .all()
        # .values(db.func.sum(Stocks.shares).label("shares"))
    )

    currentCash = db.session.query(User).filter(
        User.name == current_user.name).all()

    totalStocks = (
        db.session.query(db.func.sum(
            Stocks.shares * Stocks.price).label("totalStocks"))
        .filter(Stocks.name == current_user.name).all()
    )

    return render_template(
        "home.html",
        userStocks=userStocks,
        currentCash=currentCash,
        totalStocks=totalStocks,
    )


@main.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        flash(quote["name"])
        flash("is currently priced at")
        flash(quote["price"])
        flash("usd")
    return render_template("quote.html")


@main.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = float(request.form.get("shares"))
        quote = lookup(symbol)
        share = quote["name"]
        price = float(quote["price"])
        time = datetime.datetime.utcnow()
        name = current_user.name

        sum = price * shares

        currentUser = User.query.filter(User.id == current_user.id).all()
        for cash in currentUser:
            currentCash = cash.cash

        if (currentCash - sum) > 0:
            newCash = currentCash - sum
            newStocks = Stocks(
                name=name, share=share, shares=shares, price=price, time=time
            )

            db.session.add(newStocks)
            db.session.commit()

            update = User.query.filter_by(id=current_user.id).first()
            update.cash = newCash
            flash(update.cash)
            db.session.commit()
        else:
            flash("Not enough funds")
    return render_template("buy.html")


@main.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        negShares = float(request.form.get("shares")) * -1

        name = current_user.name
        quote = lookup(symbol)
        share = quote["name"]
        price = float(quote["price"])
        time = datetime.datetime.utcnow()
        sum = price * negShares

        currentUser = User.query.filter(User.id == current_user.id).all()
        for cash in currentUser:
            currentCash = cash.cash

        stockLookup = Stocks.query.filter(Stocks.name == name).all()
        totalStocks = 0
        for stocks in stockLookup:
            totalStocks += stocks.shares

        if (totalStocks + negShares) >= 0:
            newCash = currentCash - sum
            newStocks = Stocks(
                name=name, share=share, shares=negShares, price=price, time=time
            )

            db.session.add(newStocks)
            db.session.commit()

            update = User.query.filter_by(id=current_user.id).first()
            update.cash = newCash
            db.session.commit()
        else:
            flash("Not enough shares")
    return render_template("sell.html")


@main.route("/history", methods=["GET", "POST"])
@login_required
def history():
    userStocks = (
        db.session.query(Stocks.share, Stocks.shares, Stocks.time)
        .filter(Stocks.name == current_user.name).all()
    )
    return render_template("history.html", userStocks=userStocks)
