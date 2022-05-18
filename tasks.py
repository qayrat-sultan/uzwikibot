import logging
from datetime import timedelta

from utils import WikiApi

api = WikiApi()
interval_seconds = 10
database_list_limit = 20
channel_link = "@uzwikinewpages"


async def get_last_created_page(bot, collwikis):
    data = api.get_new_pages()

    recent_list: list = data['query']['recentchanges']
    for i in recent_list:
        i.update({
            "_id": i.get('pageid'),
        })

    # result = collwikis.insert_many(
    #     [i for i in recent_list])
    # print('result %s' % repr(result.inserted_ids))

    recent_db_list = collwikis.find({}).sort('_id', -1)
    recent_db_ids = [a.get('_id') for a in await recent_db_list.to_list(length=database_list_limit)]

    new_page_obj = []

    for x in recent_list:
        if x.get('pageid') not in recent_db_ids:
            new_page_obj.append(x)
    from datetime import datetime
    if new_page_obj:
        await collwikis.insert_many(
            [i for i in new_page_obj])
        for page in new_page_obj:
            vaqt = datetime.strptime(page['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=5)
            await bot.send_message(channel_link, "*Yangi sahifa!*\n"
                                                 "Nomi: [{title}](https://uz.wikipedia.org/wiki/{title})\n"
                                                 "Foydalanuvchi: {user}\n"
                                                 "Hajmi: {newlen}\n"
                                                 "Vaqti: {vaqt}".format(title=page['title'],
                                                                        user=page['user'],
                                                                        newlen=page['newlen'],
                                                                        vaqt=vaqt.strftime("%H:%M:%S")),
                                   parse_mode="Markdown", disable_web_page_preview=True)
    else:
        logging.info("NO CHANGES")

    return True


def set_scheduled_jobs(scheduler, *args, **kwargs):
    # Adding tasks to scheduler
    scheduler.add_job(get_last_created_page, "interval", seconds=interval_seconds, args=args)
    # scheduler.add_job(clear_notifications_per_day, "interval", seconds=10)