from flask import request, redirect, render_template, url_for
from . import events



@events.route('calendar', methods=['POST', 'GET'])
def calendar():
    return render_template('/events/calendar.html')