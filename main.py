import json
import traceback
import requests
import urllib3
import datetime
import pytz
import sqlite3
from khl import Bot, Cert, Message
from khl.card import Card, CardMessage, Module, Types, Element, Struct

session = requests.Session()
session.verify = False  # 关闭 SSL 验证
urllib3.disable_warnings()

# 打开 config.json
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 指定数据库
database = sqlite3.connect('./data.db')
data = database.cursor()


data.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yuanshen'")  
if data.fetchone():  
    print("数据表 yuanshen 已经存在，无需重复创建，故跳过创建步骤")  
else:  
    data.execute("""CREATE TABLE yuanshen (
                kuid TEXT,
                guid TEXT,
                cookies TEXT
                )
    """)

data.execute("INSERT INTO yuanshen VALUES ('1404317302', '284459282', '_MHYUUID=7c981f02-6e95-4712-81c5-dda8dd2b0e3e; _MHYUUID=7c981f02-6e95-4712-81c5-dda8dd2b0e3e; DEVICEFP_SEED_ID=e485c4dab1dc06d7; DEVICEFP_SEED_TIME=1686299114498; _ga=GA1.1.462608933.1686299115; DEVICEFP=38d7f1753b163; LOGIN_PLATFORM_COMMON_INFO={%22lifecycle_id%22:%22a524e8fc-8cbf-408f-b52d-fd04ec255646%22}; LOGIN_PLATFORM_SWITCH_STATUS={%22bll8iq97cem8%22:{%22password_reset_entry%22:true%2C%22qr_login%22:true%2C%22sms_login_tab%22:true%2C%22pwd_login_tab%22:true}}; cookie_token_v2=v2_lSH7-q_r9BEMVff6Rmsoipf1JxN0DG8IdoYA3-haeiI0uGoVFH3bt221_IGcURTf0WbnDaWVQFQ0z1YTvJXS79n4Ky6Ve3DbAU1Wr-wZR-_jKCiHdTWjqtxRLcoKuJw=; account_mid_v2=0tjt63xlqk_mhy; account_id_v2=391736026; ltoken_v2=v2_xuQW9ew0GxCx1y6J1py2WK1IS0qYIAkJmx2lTT2OlfhNK0_VPdSuPoENJ7XOwUe9WW3CVpnTPf5O4YADsfO5nKhTlA0Oq37ex0usqx9dcJfxtyDl0Og7JbMfbuDOCp4L; ltmid_v2=0tjt63xlqk_mhy; ltuid_v2=391736026; cookie_token=R7MMw0Po0PTszKZHmwOYotvrmBWeoclu76QzrrTj; account_id=391736026; ltoken=W027WVRBrC4l7cQt6Ljhn9WdXDFJ352L9jEfPqkv; ltuid=391736026; _ga_KS4J8TXSHQ=GS1.1.1700964690.48.1.1700964713.0.0.0')")

database.commit()
database.close()

# 指定时区
timezone = pytz.timezone(config["timezone"])


if config['connection_mode'] == "webhook":
    bot = Bot(cert=Cert(token=config['token'],verify_token=config['verify_token'],encrypt_key=config['encrypt_token']),port=config['webhook_port'])
elif config['connection_mode'] == "websocket":
    bot = Bot(token=config['token'])
else:
    print("Invalid Connection Mode (Valid values: websocket/webhook)")
    print("错误的连接方式（有效值: websocket/webhook）")

    
# 注册指令[/bind]
@bot.command(name='bind')
async def bind(msg: Message,uid:str,cookie:str):
    await msg.author.load()
    with open("./data/data.json", "r") as f:
        bind_file_dict = json.load(f)
    if msg.author.id in bind_file_dict:
        bind_file_dict[msg.author.id]["uid"] = uid
        bind_file_dict[msg.author.id]["cookie"] = cookie
    else:
        bind_file_dict.update({msg.author.id:{"uid":uid, "cookie":cookie}})

    with open("./data/data.json", "w") as f:
        json.dump(bind_file_dict,f)
    bindOKcard = Card(Module.Header("【原神账号绑定】绑定成功通知"),Module.Context(f'{datetime.datetime.now().astimezone(timezone)}'),Module.Section(f'你已将 原神账号`{uid}` 绑定至 KOOK@{msg.author.nickname}'),)
    await msg.reply(CardMessage(bindOKcard))

if __name__ == '__main__':
    print('银河号，启动！')
    bot.run()