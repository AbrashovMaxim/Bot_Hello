from aiogram import Bot, types, F, Router
from aiogram.types import CallbackQuery
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.enums.chat_member_status import ChatMemberStatus

from libs.db import Users, Requests, db
from libs.config import config

channels = config.get_channels()
router = Router()

# -1001939405814 - Мульт
# -1001775771244 - Сериал
# -1001779666110 - Кино
# -1002090514593 - Тихо
# id=-1002118152604

class ButtonHopper(CallbackData, prefix='buttonhopper'):
    page: int

async def checkStatus(check):
    if check.status == ChatMemberStatus.MEMBER or check.status == ChatMemberStatus.ADMINISTRATOR or check.status == ChatMemberStatus.CREATOR: return True
    else: return False

@router.message(F.text)
async def get_base_message(message: types.Message, bot: Bot):
    id_user = message.chat.id
    if not await checkStatus(await bot.get_chat_member(config.get_channel(), id_user)) and not db._exist(Requests, user_id=str(id_user)):
        main_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=config.get_url())]
            ]
        )
        await bot.send_message(id_user, "<b>Доброго времени суток </b>☄️\nЧтобы продолжить, нужно <b>подписаться</b> на канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
    await message.delete()

@router.chat_join_request()
async def join_request(update: types.ChatJoinRequest, bot: Bot):
    id_user = update.from_user.id
    if update.chat.id == config.get_channel():
        if not db._exist(Requests, user_id=str(id_user)):
            db._plus_stat("users_bot")
            db._insert(Requests(user_id=str(id_user)))

        if not db._exist(Users, user_id=str(id_user)):
            main_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Подтвердить заявку ✅", callback_data=ButtonHopper(page=1).pack())],
                    ]
                )
            message = await bot.send_message(id_user, "<b>Приветствую </b>👋\nЧтобы Вас <b>приняли</b> в канал, нужно подтвердить свою заявку, нажав кнопку снизу 👇\n\n<i>Нажимая кнопку ниже, вы даете разрешение на получение рассылок</i>", parse_mode=ParseMode.HTML, reply_markup=main_kb)
            db._insert(Users(user_id=str(id_user), from_channel=str(update.chat.id), last_message=str(message.message_id)))
        elif not db._select_One(Users, user_id=str(id_user)).is_spam:
            main_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Подтвердить заявку ✅", callback_data=ButtonHopper(page=1).pack())],
                    ]
                )
            getUser = db._select_One(Users, user_id=str(id_user))
            try: 
                if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
            except: pass
            message = await bot.send_message(id_user, "<b>Приветствую </b>👋\nЧтобы Вас <b>приняли</b> в канал, нужно подтвердить свою заявку, нажав кнопку снизу 👇\n\n<i>Нажимая кнопку ниже, вы даете разрешение на получение рассылок</i>", parse_mode=ParseMode.HTML, reply_markup=main_kb)
            db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
        else:
            getUser = db._select_One(Users, user_id=str(id_user))
            if int(getUser.to_channel) in channels.keys():
                if not await checkStatus(await bot.get_chat_member(int(getUser.to_channel), id_user)) and not channels[int(getUser.to_channel)]["DB"]._exist(Requests, user_id=str(id_user)):
                    main_kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=channels[int(getUser.to_channel)]["Url"])],
                                [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                            ]
                        )
                    try: 
                        if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                    except: pass
                    message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                    db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
                    return
                else:
                    if db._exist(Requests, user_id=str(id_user)):
                        await bot.approve_chat_join_request(config.get_channel(), id_user)
                        db._delete(Requests, user_id=str(id_user))
                        try:
                            await bot.edit_message_text("<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", id_user, int(getUser.last_message), parse_mode=ParseMode.HTML)
                        except:
                            try: 
                                if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                            except: pass
                            message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                            db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
            else:
                for i,j in channels.items():
                    if i != int(getUser.from_channel):
                        if not j["DB"]._exist(Requests, user_id=str(id_user)) and not await checkStatus(await bot.get_chat_member(i, id_user)):
                            main_kb = InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=j["Url"])],
                                    [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                                ]
                            )
                            try: 
                                if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                            except: pass
                            message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                            db._update(Users, {'last_message': str(message.message_id), 'to_channel': str(i)}, user_id=str(id_user))
                            return
                if db._exist(Requests, user_id=str(id_user)):
                    await bot.approve_chat_join_request(config.get_channel(), id_user)
                    db._delete(Requests, user_id=str(id_user))
                    try: 
                        if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                    except: pass
                    message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                    db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
                        

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    if event.chat.id == config.get_channel(): db._plus_stat("users_left")

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    if event.chat.id == config.get_channel(): db._plus_stat("users_join")

@router.callback_query(ButtonHopper.filter())
async def check_sub_handler(call: CallbackQuery, callback_data: ButtonHopper, bot: Bot):
    print(call)
    id_user = call.message.chat.id
    page = int(callback_data.page)
    
    if page == 1:
        db._plus_stat("users_spam")
        db._update(Users, {'is_spam': True}, user_id=str(call.message.chat.id))
        getUser = db._select_One(Users, user_id=str(id_user))
        if int(getUser.to_channel) in channels.keys():
            if not await checkStatus(await bot.get_chat_member(int(getUser.to_channel), id_user)) and not channels[getUser.to_channel]["DB"]._exist(Requests, user_id=str(id_user)):
                main_kb = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=channels[int(getUser.to_channel)]["Url"])],
                            [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                        ]
                    )
                try: 
                    if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                except: pass
                message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
                return
            else:
                if db._exist(Requests, user_id=str(id_user)):
                    await bot.approve_chat_join_request(config.get_channel(), id_user)
                    db._delete(Requests, user_id=str(id_user))
                    try: 
                        if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                    except: pass
                    message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                    db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
        else:
            for i,j in channels.items():
                if i != int(getUser.from_channel):
                    if not j["DB"]._exist(Requests, user_id=str(id_user)) and not await checkStatus(await bot.get_chat_member(i, id_user)):
                        main_kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=j["Url"])],
                                [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                            ]
                        )
                        try: 
                            if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                        except: pass
                        message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                        db._update(Users, {'last_message': str(message.message_id), 'to_channel': str(i)}, user_id=str(id_user))
                        return
            if db._exist(Requests, user_id=str(id_user)):
                await bot.approve_chat_join_request(config.get_channel(), id_user)
                db._delete(Requests, user_id=str(id_user))
                try: 
                    if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                except: pass
                message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
    elif page == 2:
        getUser = db._select_One(Users, user_id=str(id_user))
        if int(getUser.to_channel) in channels.keys():
            if not await checkStatus(await bot.get_chat_member(int(getUser.to_channel), id_user)) and not channels[int(getUser.to_channel)]["DB"]._exist(Requests, user_id=str(id_user)):
                main_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=channels[int(getUser.to_channel)]["Url"])],
                        [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                    ]
                )
                try: 
                    if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                except: pass
                message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                db._update(Users, {'last_message': str(message.message_id)})
                return

            else:
                if db._exist(Requests, user_id=str(id_user)):
                    await bot.approve_chat_join_request(config.get_channel(), id_user)
                    db._delete(Requests, user_id=str(id_user))
                    try: 
                        if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                    except: pass
                    message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                    db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))
        else:
            for i,j in channels.items():
                if i != int(getUser.from_channel):
                    if not j["DB"]._exist(Requests, user_id=str(id_user)) and not await checkStatus(await bot.get_chat_member(i, id_user)):
                        main_kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="👀 Перейти в канал 👀", url=j["Url"])],
                                [InlineKeyboardButton(text="💫 Проверить подписку 💫", callback_data=ButtonHopper(page=2).pack())],
                            ]
                        )
                        try: 
                            if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                        except: pass
                        message = await bot.send_message(id_user, "<b>Последний шаг </b>😊\nЧтобы Вас <b>приняли</b> в канал, нужно подписаться на партнерский канал 👇", parse_mode=ParseMode.HTML, reply_markup=main_kb)
                        db._update(Users, {'last_message': str(message.message_id), 'to_channel': str(i)}, user_id=str(id_user))
                        return
            if db._exist(Requests, user_id=str(id_user)):
                await bot.approve_chat_join_request(config.get_channel(), id_user)
                db._delete(Requests, user_id=str(id_user))
                try: 
                    if getUser.last_message != None: await bot.delete_message(int(getUser.last_message))
                except: pass
                message = await bot.send_message(id_user, "<b>Поздравляем </b>✨\nПриятного просмотра канала 💥", parse_mode=ParseMode.HTML)
                db._update(Users, {'last_message': str(message.message_id)}, user_id=str(id_user))