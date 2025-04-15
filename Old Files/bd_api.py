from string import Template
from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from loguru import logger

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_acc(self, acc_name: str, type: str, source: str, source_farming: str, login: str, psw: str,
                      email_login: str, email_psw: str, date_birth, token: str, user_agent: str, web_gl: str,
                      rk_id: str, f2a: str, type_comment: str, cookie, cost, cost_cur: str, geo: str):
        sql = 'INSERT INTO accs_data(acc_name, type, source, source_farming, login, psw, email_login, email_psw,' \
              'date_birth, token, user_agent, web_gl, rk_id, f2a, type_comment, cookie, cost, cost_cur, geo)' \
              ' VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19) ' \
              'returning *'
        return await self.execute(sql, acc_name, type, source, source_farming, login, psw, email_login, email_psw,
              date_birth, token, user_agent, web_gl, rk_id, f2a, type_comment, cookie, cost, cost_cur, geo,
                                  fetchrow=True)

    async def add_click_bd(self, acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt: int, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, offer_name, landing_name, from_tranzit):
        sql = ('INSERT INTO clicks_log(acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, offer_name, landing_name, from_tranzit) '
               'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19) returning *')
        return await self.execute(sql, acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, offer_name, landing_name, from_tranzit, fetchrow=True)

    async def add_click_tranzit_bd(self, acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt: int, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, tranzit: bool, tranzit_name, offer_name):
        sql = ('INSERT INTO clicks_log(acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, tranzit, tranzit_name, offer_name) '
               'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19) returning *')
        return await self.execute(sql, acc_id, rk_id, creo_id, type_optim, fb_pixel_id, camp_id_kt, ip, user_agent, device, browser, domain, region, city, country, isp, org_as, tranzit, tranzit_name, offer_name, fetchrow=True)

    async def add_conversion_bd(self, click_id, name, phone, ip, user_agent, domain, status, country, offer_name, landing_name, tranzit_name):
        sql = ('INSERT INTO conversions_log(click_id, name, phone, ip, user_agent, domain, status, country, offer_name, landing_name, tranzit_name) '
               'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) returning *')
        return await self.execute(sql, click_id, name, phone, ip, user_agent, domain, status, country, offer_name, landing_name, tranzit_name, fetchrow=True)

    async def add_nutra_kpi(self, kt_campaign_id: int, kt_campaign_name: str, link_camp: str, type: str, send_to: list):
        sql = ('INSERT INTO kpi_controller(kt_campaign_id, kt_campaign_name, link_camp, type, send_to) '
               'VALUES ($1, $2, $3, $4, $5) returning *')
        return await self.execute(sql, kt_campaign_id, kt_campaign_name, link_camp, type, send_to, fetchrow=True)

    async def add_bin(self, card_service_name: str, card_service_priority: int, bin: str, bin_status: str, bin_geo: str, bin_3ds, bin_info: str, bin_cur: str, is_active_on_service, service_bin_id):
        sql = ('INSERT INTO cards_bins_info(card_service_name, card_service_priority, bin, bin_status, bin_geo, bin_3ds, bin_info, bin_cur, is_active_on_service, service_bin_id) '
               'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) returning *')
        return await self.execute(sql, card_service_name, card_service_priority, bin, bin_status, bin_geo, bin_3ds, bin_info, bin_cur, is_active_on_service, service_bin_id, fetchrow=True)

    async def update_bin(self, bin, card_service_name, card_service_priority, bin_geo, bin_3ds, bin_info, bin_cur, is_active_on_service, service_bin_id):
        sql = 'UPDATE cards_bins_info SET card_service_priority=$3, bin_geo=$4, bin_3ds=$5, bin_info=$6, bin_cur=$7, is_active_on_service=$8, service_bin_id=$9  WHERE bin=$1 AND card_service_name=$2 returning *'
        return await self.execute(sql, bin, card_service_name, card_service_priority, bin_geo, bin_3ds, bin_info, bin_cur, is_active_on_service, service_bin_id, fetchrow=True)

    async def add_proxy_bd(self, ip, type, login, psw, date_start, date_end, port_socks5, port_https, geo, link_change_ip, status, proxy_cost, proxy_cur):
        sql = 'INSERT INTO proxy_data(ip, type, login, psw, date_start, date_end, port_socks5, port_https, geo, link_change_ip, status, proxy_cost, proxy_cur) ' \
              'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) returning *'
        return await self.execute(sql, ip, type, login, psw, date_start, date_end, port_socks5, port_https, geo, link_change_ip, status, proxy_cost, proxy_cur,
                                  fetchrow=True)

    async def add_conv_file_bd(self, source, first_name, last_name, email, phone, country, zip, city, gender, birthday_date, user_agent, ip, conversion_type):
        sql = 'INSERT INTO coversions_data_log(source, first_name, last_name, email, phone, country, zip, city, gender, birthday_date, user_agent, ip, conversion_type) ' \
              'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) returning *'
        return await self.execute(sql, source, first_name, last_name, email, phone, country, zip, city, gender, birthday_date, user_agent, ip, conversion_type,
                                  fetchrow=True)



    async def add_cookie(self, acc_name, cookie):
        sql = 'UPDATE accs_data SET cookie=$2 WHERE acc_name=$1 returning *'
        return await self.execute(sql, acc_name, cookie, fetchrow=True)


    async def update_rk_list(self, id_acc_bd: int, rk_list):
        sql = 'UPDATE accs_data SET rk_list=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, rk_list, fetchrow=True)

    async def update_proxy_uuid_octo(self, for_octo: bool, octo_uuid: str, proxy_id: int):
        sql = 'UPDATE proxy_data SET octo_uuid=$2, for_octo=$1 WHERE proxy_id=$3 returning *'
        return await self.execute(sql, for_octo, octo_uuid, proxy_id, execute=True)

    async def select_free_proxy_by_geo(self, geo: str, status: str, type: str):
        sql = 'SELECT * FROM proxy_data WHERE geo=$1 AND status=$2 AND type=$3'
        return await self.execute(sql, geo, status, type, fetch=True)

    async def select_conv_data_log(self, ip, email):
        sql = 'SELECT * FROM coversions_data_log WHERE ip=$1 AND email=$2'
        return await self.execute(sql, ip, email, fetch=True)

    async def update_status_proxy(self, proxy_id: int, status: str):
        sql = 'UPDATE proxy_data SET status=$2 WHERE proxy_id=$1'
        return await self.execute(sql, proxy_id, status, fetchrow=True)

    async def update_accs_list_proxy(self, proxy_id: int, accs: int):
        logger.info(f'proxy_id:{proxy_id} {type(proxy_id)}\n'
                    f'accs:{accs} {type(accs)}')
        sql = 'UPDATE proxy_data SET accs=$2 WHERE proxy_id=$1'
        return await self.execute(sql, proxy_id, accs, fetchrow=True)

    async def get_proxy_bd(self, proxy_id: int):
        sql = "SELECT * FROM proxy_data WHERE proxy_id=$1"
        return await self.execute(sql, proxy_id, fetchrow=True)

    async def get_all_proxy(self):
        sql = 'SELECT * FROM proxy_data'
        return await self.execute(sql, fetch=True)

    async def get_conv_geo_list(self):
        sql = 'SELECT DISTINCT country FROM coversions_data_log ORDER BY country;'
        return await self.execute(sql, fetch=True)

    async def get_all_conv_by_geo_in_db(self, geo):
        sql = 'SELECT * FROM coversions_data_log WHERE country=$1'
        return await self.execute(sql, geo, fetch=True)

    async def get_all_false_send_conv(self):
        sql = 'SELECT * FROM conversions_log WHERE keitara=FALSE'
        return await self.execute(sql, fetch=True)

    async def get_all_cards(self):
        sql = 'SELECT * FROM cards_data'
        return await self.execute(sql, fetch=True)

    async def get_all_cards_services(self):
        sql = 'SELECT * FROM cards_services_info'
        return await self.execute(sql, fetch=True)

    async def get_card_by_number(self, number: str):
        sql = 'SELECT * FROM cards_data WHERE number=$1'
        return await self.execute(sql, number, fetchrow=True)

    async def get_card_by_card_id(self, id_card: int):
        sql = 'SELECT * FROM cards_data WHERE id_card=$1'
        return await self.execute(sql, id_card, fetchrow=True)

    async def get_proxy_by_acc_id(self, accs: int):
        sql = "SELECT * FROM proxy_data WHERE accs=$1"
        return await self.execute(sql, accs, fetchrow=True)

    async def get_mob_octo_proxy(self, geo):
        sql = "SELECT * FROM proxy_data WHERE geo=$1"
        return await self.execute(sql, geo, fetch=True)

    async def get_kpi_controller_by_camp_id(self, kt_campaign_id):
        sql = "SELECT * FROM kpi_controller WHERE kt_campaign_id=$1"
        return await self.execute(sql, kt_campaign_id, fetchrow=True)

    async def get_kpi_controller_by_kpi_id(self, kpi_id):
        sql = "SELECT * FROM kpi_controller WHERE id=$1"
        return await self.execute(sql, kpi_id, fetchrow=True)

    async def get_kpi_controller_all(self):
        sql = "SELECT * FROM kpi_controller"
        return await self.execute(sql, fetch=True)

    async def get_offers_rates_all(self):
        sql = "SELECT * FROM offers_rates"
        return await self.execute(sql, fetch=True)

    async def get_kpi_controller_by_camp_id_creo_id_type_optim(self, kt_campaign_id, creo_id, type_optimization):
        sql = "SELECT * FROM kpi_controller WHERE kt_campaign_id=$1 AND creo_id=$2 AND type_optimization=$3"
        return await self.execute(sql, kt_campaign_id, creo_id, type_optimization, fetchrow=True)

    async def get_kpi_controller_by_camp_id_type_optim(self, kt_campaign_id, type_optimization):
        sql = "SELECT * FROM kpi_controller WHERE kt_campaign_id=$1 AND type_optimization=$2"
        return await self.execute(sql, kt_campaign_id, type_optimization, fetchrow=True)

    async def get_kpi_controller_by_camp_id_creo(self, kt_campaign_id, creo_id):
        sql = "SELECT * FROM kpi_controller WHERE kt_campaign_id=$1 AND creo_id=$2"
        return await self.execute(sql, kt_campaign_id, creo_id, fetchrow=True)

    async def get_all_accs_by_type(self, type: str):
        '''

        :param type: - есть два вида king и avtoreg
        :return:
        '''
        sql = 'SELECT * FROM accs_data WHERE type=$1'
        return await self.execute(sql, type, fetch=True)

    async def get_all_accs_by_kt_camp_id(self, kt_campaign_id):
        '''

        :param type: - есть два вида king и avtoreg
        :return:
        '''
        sql = 'SELECT * FROM accs_data WHERE kt_campaign_id=$1'
        return await self.execute(sql, kt_campaign_id, fetch=True)

    async def get_all_accs_by_type_active(self, type: str):
        '''

        :param type: - есть два вида king и avtoreg
        :return:
        '''
        sql = "SELECT * FROM accs_data WHERE type=$1 AND (status='ACTIVE' OR status='PendingUnban')"
        return await self.execute(sql, type, fetch=True)

    async def get_free_proxy_by_geo(self, geo, status, type):
        sql = 'SELECT * FROM proxy_data WHERE geo=$1 AND status=$2 AND type=$3'
        return await self.execute(sql, geo, status, type, fetch=True)

    async def get_free_proxy(self, status):
        sql = 'SELECT * FROM proxy_data WHERE status=$1'
        return await self.execute(sql, status, fetch=True)

    async def get_card_service_data_by_name(self, name):
        sql = 'SELECT * FROM cards_services_info WHERE card_service_name=$1'
        return await self.execute(sql, name, fetchrow=True)

    async def get_bin_by_name(self, bin_name, service_name):
        sql = 'SELECT * FROM cards_bins_info WHERE bin=$1 AND card_service_name=$2'
        return await self.execute(sql, bin_name, service_name, fetchrow=True)

    async def get_acc_bd(self, id_acc_bd: int):
        sql = "SELECT * FROM accs_data WHERE id_acc_bd=$1"
        return await self.execute(sql, id_acc_bd, fetchrow=True)

    async def get_acc_bd_by_name(self, acc_name: str):
        sql = "SELECT * FROM accs_data WHERE acc_name=$1"
        return await self.execute(sql, acc_name, fetchrow=True)

    async def get_acc_bd_by_id(self, id: int):
        sql = "SELECT * FROM accs_data WHERE id_acc_bd=$1"
        return await self.execute(sql, id, fetchrow=True)

    async def get_acc_by_vertical(self, vertical):
        sql = "SELECT * FROM accs_data WHERE vertical=$1"
        return await self.execute(sql, vertical, fetch=True)

    async def get_ip_data_by_acc_id(self, accs: int):
        sql = 'SELECT * FROM proxy_data WHERE accs=$1'
        return await self.execute(sql, accs, fetchrow=True)

    async def get_ip_data_by_ip(self, ip: str):
        sql = 'SELECT * FROM proxy_data WHERE ip=$1'
        return await self.execute(sql, ip, fetchrow=True)

    async def get_click_data_by_ip(self, ip: str):
        sql = 'SELECT * FROM clicks_log WHERE ip=$1'
        return await self.execute(sql, ip, fetchrow=True)

    async def get_click_data_by_click_id(self, click_id):
        sql = 'SELECT * FROM clicks_log WHERE click_id=$1'
        return await self.execute(sql, click_id, fetchrow=True)

    async def get_conv_data_by_ip(self, ip: str):
        sql = 'SELECT * FROM conversions_log WHERE ip=$1'
        return await self.execute(sql, ip, fetchrow=True)

    async def get_click_data_by_ip_tranzit(self, ip: str):
        sql = 'SELECT * FROM clicks_log WHERE ip=$1 AND tranzit=TRUE'
        return await self.execute(sql, ip, fetchrow=True)

    async def get_click_data_by_creo_id_tranzitname(self, rk: str, creo_id: str, tranzit_name:str):
        sql = 'SELECT COUNT(*) FROM clicks_log WHERE rk_id=$1 AND tranzit=TRUE AND creo_id=$2 AND tranzit_name=$3'
        return await self.execute(sql,rk, creo_id, tranzit_name, fetchval=True)

    async def get_click_data_rk_tranzit(self, rk: str):
        sql = 'SELECT * FROM clicks_log WHERE rk_id=$1 AND tranzit=TRUE'
        return await self.execute(sql, rk, fetch=True)

    async def get_click_data_by_ip_not_tranzit(self, ip: str):
        sql = 'SELECT * FROM clicks_log WHERE ip=$1 AND tranzit IS NULL'
        return await self.execute(sql, ip, fetchrow=True)

    async def get_adv_data_by_name(self, adv_name: str):
        sql = 'SELECT * FROM api_advertisers WHERE adv_name=$1'
        return await self.execute(sql, adv_name, fetchrow=True)

    async def get_rates_data_by_offer_id(self, offer_id_kt: int):
        sql = 'SELECT * FROM offers_rates WHERE offer_id_kt=$1'
        return await self.execute(sql, offer_id_kt, fetchrow=True)

    async def get_daily_stat_rk(self, rk_id, date_log):
        sql = 'SELECT * FROM rk_data_daily WHERE rk_id=$1 AND date_log=$2'
        return await self.execute(sql, rk_id, date_log, fetchrow=True)

    async def get_deily_stat_ad(self, ad_id, date_log):
        sql = 'SELECT * FROM ad_data_daily WHERE ad_id=$1 AND date_log=$2'
        return await self.execute(sql, ad_id, date_log, fetchrow=True)

    async def get_daily_stat_all_rk_by_date(self, date_log):
        sql = 'SELECT * FROM rk_data_daily WHERE date_log=$1'
        return await self.execute(sql, date_log, fetch=True)

    async def get_daily_stat_all_rk_by_date_and_kt_camp_id(self, date_log, kt_campaign_id):
        sql = 'SELECT * FROM rk_data_daily WHERE date_log=$1 AND kt_campaign_id=$2'
        return await self.execute(sql, date_log, kt_campaign_id, fetch=True)

    async def get_daily_stat_all_rk_by_date(self, date_log):
        sql = 'SELECT * FROM rk_data_daily WHERE date_log=$1'
        return await self.execute(sql, date_log, fetch=True)

    async def get_stat_all_rk_by_date(self):
        sql = 'SELECT * FROM rk_data'
        return await self.execute(sql, fetch=True)

    async def get_stat_all_rk_daily(self):
        sql = 'SELECT * FROM rk_data_daily'
        return await self.execute(sql, fetch=True)

    async def get_stat_all_rk(self):
        sql = 'SELECT * FROM rk_data'
        return await self.execute(sql, fetch=True)

    async def get_stat_all_rk_by_status(self, live_status):
        sql = 'SELECT * FROM rk_data WHERE live_status=$1'
        return await self.execute(sql, live_status, fetch=True)

    async def get_stat_all_rk_by_campaign_id(self, kt_campaign_id):
        sql = 'SELECT * FROM rk_data WHERE kt_campaign_id=$1'
        return await self.execute(sql, kt_campaign_id, fetch=True)

    async def get_stat_all_rk_by_campaign_id_daily(self, kt_campaign_id):
        sql = 'SELECT * FROM rk_data_daily WHERE kt_campaign_id=$1'
        return await self.execute(sql, kt_campaign_id, fetch=True)

    async def get_stat_rk(self, rk_id: str):
        sql = 'SELECT * FROM rk_data WHERE rk_id=$1'
        return await self.execute(sql, rk_id, fetchrow=True)

    async def get_stat_ad(self, ad_id: str):
        sql = 'SELECT * FROM ad_data WHERE ad_id=$1'
        return await self.execute(sql, ad_id, fetchrow=True)

    async def get_stat_rk_by_account_id(self, account_id):
        sql = 'SELECT * FROM rk_data WHERE rk_id=$1'
        return await self.execute(sql, account_id, fetchrow=True)

    async def get_stat_ad_by_ad_id(self, account_id):
        sql = 'SELECT * FROM ad_data WHERE ad_id=$1'
        return await self.execute(sql, account_id, fetchrow=True)


    async def add_acc_fbt(self, id_acc_bd: int, acc_name: str, fbt_acc_id: int, fbt_proxy_id: int, proxy_id: int):
        sql = "INSERT INTO fbt_acc_data(id_acc_bd, acc_name, fbt_acc_id, fbt_proxy_id, proxy_id) " \
              "VALUES ($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, id_acc_bd, acc_name, fbt_acc_id, fbt_proxy_id, proxy_id, fetchrow=True)

    async def add_rk_daily_stat(self, rk_id, date_log):
        sql = 'INSERT INTO rk_data_daily(rk_id, date_log) VALUES ($1, $2) returning *'
        return await self.execute(sql, rk_id, date_log, fetchrow=True)

    async def add_ad_daily_stat(self, rk_id, date_log, ad_id, id_acc_bd, camp_id, adset_id):
        sql = 'INSERT INTO ad_data_daily(rk_id, date_log, ad_id, id_acc_bd, camp_id, adset_id) VALUES ($1, $2, $3, $4, $5, $6) returning *'
        return await self.execute(sql, rk_id, date_log, ad_id, id_acc_bd, camp_id, adset_id, fetchrow=True)

    async def add_card_in_bd(self, id_card_adscards: int, number: str, ads_limit, balance, date_card: str, cvc: str, adscard_status: str, issued: str, adscard_guid: str, comment: str, currency_type: str):
        sql = 'INSERT INTO cards_data(id_card_adscards, number, ads_limit, balance, date_card, cvc, adscard_status, issued, adscard_guid, comment, currency_type) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) returning *'
        return await self.execute(sql, id_card_adscards, number, ads_limit, balance, date_card, cvc, adscard_status, issued, adscard_guid, comment, currency_type, fetchrow=True)

    async def add_rk_daily_stat_with_camp_id(self, rk_id, date_log, kt_campaign_id):
        sql = 'INSERT INTO rk_data_daily(rk_id, date_log, kt_campaign_id) VALUES ($1, $2, $3) returning *'
        return await self.execute(sql, rk_id, date_log, kt_campaign_id, fetchrow=True)

    async def add_rk_stat(self, rk_id, id_acc_bd):
        sql = 'INSERT INTO rk_data(rk_id, id_acc_bd) VALUES ($1, $2) returning *'
        return await self.execute(sql, rk_id, id_acc_bd, fetchrow=True)

    async def add_ad_stat(self, rk_id, id_acc_bd, camp_id, adset_id, ad_id):
        sql = 'INSERT INTO ad_data(rk_id, id_acc_bd, camp_id, adset_id, ad_id) VALUES ($1, $2, $3, $4, $5) returning *'
        return await self.execute(sql, rk_id, id_acc_bd, camp_id, adset_id, ad_id, fetchrow=True)

    async def add_rk_stat_with_status(self, rk_id, id_acc_bd, live_status):
        sql = 'INSERT INTO rk_data(rk_id, id_acc_bd, live_status) VALUES ($1, $2, $3) returning *'
        return await self.execute(sql, rk_id, id_acc_bd, live_status, fetchrow=True)


    async def update_rk_daily_stat(self, rk_id: str, date_log, fb_effective_status: str, fb_status: str, fb_clicks: int, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update, time_zone):
        sql = 'UPDATE rk_data_daily SET fb_effective_status=$3, fb_status=$4, fb_clicks=$5, fb_cost_per_unique_click=$6, fb_cpc=$7, fb_cpm=$8, fb_ctr=$9, fb_impressions=$10, fb_objective=$11, fb_spend=$12, fb_quality_score_organic=$13, fb_quality_score_ectr=$14, fb_quality_score_ecvr=$15, fb_link_click=$16, fb_video_view=$17, fb_page_engagement=$18, fb_post_engagement=$19, fb_post_reaction=$20, last_update=$21, time_zone=$22  WHERE rk_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, fb_effective_status, fb_status, fb_clicks, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update, time_zone, execute=True)

    async def update_ad_daily_stat(self, rk_id: str, date_log, fb_effective_status: str, fb_status: str, fb_clicks: int, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update, time_zone, ad_id):
        sql = 'UPDATE ad_data_daily SET fb_effective_status=$3, fb_status=$4, fb_clicks=$5, fb_cost_per_unique_click=$6, fb_cpc=$7, fb_cpm=$8, fb_ctr=$9, fb_impressions=$10, fb_objective=$11, fb_spend=$12, fb_quality_score_organic=$13, fb_quality_score_ectr=$14, fb_quality_score_ecvr=$15, fb_link_click=$16, fb_video_view=$17, fb_page_engagement=$18, fb_post_engagement=$19, fb_post_reaction=$20, last_update=$21, time_zone=$22, rk_id=$1  WHERE ad_id=$23 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, fb_effective_status, fb_status, fb_clicks, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update, time_zone, ad_id, execute=True)

    async def update_rk_daily_spend(self, rk_id: str, date_log, fb_spend):
        sql = 'UPDATE rk_data_daily SET fb_spend=$3 WHERE rk_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, fb_spend, fetchrow=True)

    async def update_rk_daily_campaign_id(self, rk_id: str, date_log, kt_campaign_id):
        sql = 'UPDATE rk_data_daily SET kt_campaign_id=$3 WHERE rk_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, kt_campaign_id, fetchrow=True)

    async def update_rk_daily_comment(self, rk_id: str, comment):
        sql = 'UPDATE rk_data_daily SET comment=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, comment, fetchrow=True)

    async def update_rk_comment(self, rk_id: str, comment):
        sql = 'UPDATE rk_data SET comment=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, comment, fetchrow=True)

    async def update_rk_cards(self, rk_id: str, cards):
        sql = 'UPDATE rk_data SET cards=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, cards, fetchrow=True)

    # async def update_acc_fp(self, rk_id: str, comment):
    #     sql = 'UPDATE rk_data SET comment=$2 WHERE rk_id=$1 returning *'
    #     return await self.execute(sql, rk_id, comment, fetchrow=True)

    async def update_card_spend(self, adscard_guid, total_withdrawal, total_replenishment, total_pending, total_issued, total_commision):
        sql = 'UPDATE cards_data SET total_withdrawal=$2, total_replenishment=$3, total_pending=$4, total_issued=$5, total_commision=$6 WHERE adscard_guid=$1 returning *'
        return await self.execute(sql, adscard_guid, total_withdrawal, total_replenishment, total_pending, total_issued, total_commision, fetchrow=True)

    async def update_rk_spend_warm(self, rk_id: str, spend_warm):
        sql = 'UPDATE rk_data SET spend_warm=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, spend_warm, fetchrow=True)

    async def update_rk_spend_total(self, rk_id: str, fb_spend):
        sql = 'UPDATE rk_data SET fb_spend=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, fb_spend, fetchrow=True)

    async def update_rk_daily_live_status(self, rk_id: str, live_status):
        sql = 'UPDATE rk_data_daily SET live_status=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, live_status, fetchrow=True)

    async def update_rk_live_status(self, rk_id: str, live_status):
        sql = 'UPDATE rk_data SET live_status=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, live_status, fetchrow=True)

    async def update_rk_ad_id(self, rk_id: str, ad_id):
        sql = 'UPDATE rk_data SET ad_id=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, ad_id, fetchrow=True)

    async def update_pixel_ad_id(self, rk_id: str, pixel_id):
        sql = 'UPDATE rk_data SET pixel_id=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, pixel_id, fetchrow=True)

    async def update_pixel_ad_token(self, rk_id: str, pixel_token):
        sql = 'UPDATE rk_data SET pixel_token=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, pixel_token, fetchrow=True)

    async def update_keitaro_status_in_conversions(self, click_id: str, keitara: bool):
        sql = 'UPDATE conversions_log SET keitara=$2 WHERE click_id=$1 returning *'
        return await self.execute(sql, click_id, keitara, fetchrow=True)

    async def update_kpi_cpi(self, cpi, kpi_id: int):
        sql = f'UPDATE kpi_controller SET cpi=$1 WHERE id=$2'
        logger.info(f'sql:{sql}')
        return await self.execute(sql, cpi, kpi_id, fetchrow=True)

    async def update_conversion_kt_subid(self, kt_subid, click_id: str):
        sql = f'UPDATE conversions_log SET kt_subid=$1 WHERE click_id=$2'
        return await self.execute(sql, kt_subid, click_id, fetchrow=True)

    async def update_send_to_conversion(self, send_to, click_id: str):
        sql = f'UPDATE conversions_log SET send_to=$1 WHERE click_id=$2'
        return await self.execute(sql, send_to, click_id, fetchrow=True)

    async def update_kpi_cpr(self, cpr, kpi_id: int):
        sql = f'UPDATE kpi_controller SET cpr=$1 WHERE id=$2'
        logger.info(f'sql:{sql}')
        return await self.execute(sql, cpr, kpi_id, fetchrow=True)

    async def update_kpi_cps(self, cps, kpi_id: int):
        sql = f'UPDATE kpi_controller SET cps=$1 WHERE id=$2'
        logger.info(f'sql:{sql}')
        return await self.execute(sql, cps, kpi_id, fetchrow=True)

    async def update_rk_geo_buying(self, rk_id: str, geo_buying):
        sql = 'UPDATE rk_data SET geo_buying=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, geo_buying, fetchrow=True)

    async def update_rk_vertical(self, rk_id: str, vertical):
        sql = 'UPDATE rk_data SET vertical=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, vertical, fetchrow=True)

    async def update_rk_daily_geo_buying(self, rk_id: str, geo_buying, date_log):
        sql = 'UPDATE rk_data_daily SET geo_buying=$2 WHERE rk_id=$1 AND date_log=$3 returning *'
        return await self.execute(sql, rk_id, geo_buying, date_log, fetchrow=True)

    async def update_rk_type_optimization(self, rk_id: str, type_optimization):
        sql = 'UPDATE rk_data SET type_optimization=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, type_optimization, fetchrow=True)

    async def update_rk_daily_type_optimization(self, rk_id: str, type_optimization, date_log):
        sql = 'UPDATE rk_data_daily SET type_optimization=$2 WHERE rk_id=$1 AND date_log=$3 returning *'
        return await self.execute(sql, rk_id, type_optimization, date_log, fetchrow=True)

    async def update_rk_kt_campaign_name(self, rk_id: str, kt_campaign_name):
        sql = 'UPDATE rk_data SET kt_campaign_name=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, kt_campaign_name, fetchrow=True)

    async def update_rk_daily_kt_campaign_name(self, rk_id: str, kt_campaign_name, date_log):
        sql = 'UPDATE rk_data_daily SET kt_campaign_name=$2 WHERE rk_id=$1 AND date_log=$3 returning *'
        return await self.execute(sql, rk_id, kt_campaign_name, date_log, fetchrow=True)

    async def update_rk_install_or_dep(self, rk_id: str, install_or_dep):
        sql = 'UPDATE rk_data SET install_or_dep=$2 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, install_or_dep, fetchrow=True)

    async def update_acc_fp(self, id_acc_bd: int, fp: str):
        sql = 'UPDATE accs_data SET fp=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, fp, fetchrow=True)

    async def update_rk_stat_fbt(self, rk_id: str, fb_effective_status: str, fb_status: str, fb_clicks: int, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update_fbt, time_zone):
        sql = 'UPDATE rk_data SET fb_effective_status=$2, fb_status=$3, fb_clicks=$4, fb_cost_per_unique_click=$5, fb_cpc=$6, fb_cpm=$7, fb_ctr=$8, fb_impressions=$9, fb_objective=$10, fb_spend=$11, fb_quality_score_organic=$12, fb_quality_score_ectr=$13, fb_quality_score_ecvr=$14, fb_link_click=$15, fb_video_view=$16, fb_page_engagement=$17, fb_post_engagement=$18, fb_post_reaction=$19, last_update_fbt=$20, time_zone=$21  WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, fb_effective_status, fb_status, fb_clicks, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update_fbt, time_zone, execute=True)

    async def update_ad_stat_fbt(self, ad_id: str, fb_effective_status: str, fb_status: str, fb_clicks: int, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update_fbt, time_zone):
        sql = 'UPDATE ad_data SET fb_effective_status=$2, fb_status=$3, fb_clicks=$4, fb_cost_per_unique_click=$5, fb_cpc=$6, fb_cpm=$7, fb_ctr=$8, fb_impressions=$9, fb_objective=$10, fb_spend=$11, fb_quality_score_organic=$12, fb_quality_score_ectr=$13, fb_quality_score_ecvr=$14, fb_link_click=$15, fb_video_view=$16, fb_page_engagement=$17, fb_post_engagement=$18, fb_post_reaction=$19, last_update_fbt=$20, time_zone=$21  WHERE ad_id=$1 returning *'
        return await self.execute(sql, ad_id, fb_effective_status, fb_status, fb_clicks, fb_cost_per_unique_click, fb_cpc, fb_cpm, fb_ctr, fb_impressions, fb_objective, fb_spend, fb_quality_score_organic, fb_quality_score_ectr, fb_quality_score_ecvr, fb_link_click, fb_video_view, fb_page_engagement, fb_post_engagement, fb_post_reaction, last_update_fbt, time_zone, execute=True)

    async def update_kr_daily_stat_kt(self, rk_id: str, date_log, regs: int, deps: int, last_update_kt, kt_unic_clicks):
        sql = 'UPDATE rk_data_daily SET regs=$3, deps=$4, last_update_kt=$5, kt_unic_clicks=$6 WHERE rk_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, regs, deps, last_update_kt, kt_unic_clicks, execute=True)

    async def update_ad_daily_stat_kt(self, ad_id: str, date_log, regs: int, deps: int, last_update_kt, kt_unic_clicks):
        sql = 'UPDATE ad_data_daily SET regs=$3, deps=$4, last_update_kt=$5, kt_unic_clicks=$6 WHERE ad_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, ad_id, date_log, regs, deps, last_update_kt, kt_unic_clicks, execute=True)

    async def update_rk_stat_kt(self, rk_id: str, regs: int, deps: int, last_update_kt, kt_unic_clicks):
        sql = 'UPDATE rk_data SET regs=$2, deps=$3, last_update_kt=$4, kt_unic_clicks=$5 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, regs, deps, last_update_kt, kt_unic_clicks, execute=True)

    async def update_ad_stat_kt(self, ad_id: str, regs: int, deps: int, last_update_kt, kt_unic_clicks):
        sql = 'UPDATE ad_data SET regs=$2, deps=$3, last_update_kt=$4, kt_unic_clicks=$5 WHERE ad_id=$1 returning *'
        return await self.execute(sql, ad_id, regs, deps, last_update_kt, kt_unic_clicks, execute=True)

    async def update_metrics_rk_daily_stat(self, rk_id, date_log, i2r, cpi, cr2r, cpr, cr2d, r2s, cps, broi, income, bprofit, c2i, cr2i):
        sql = 'UPDATE rk_data_daily SET i2r=$3, cpi=$4, cr2r=$5, cpr=$6, cr2d=$7, r2s=$8, cps=$9, broi=$10, income=$11, bprofit=$12, c2i=$13, cr2i=$14 WHERE rk_id=$1 AND date_log=$2 returning *'
        return await self.execute(sql, rk_id, date_log, i2r, cpi, cr2r, cpr, cr2d, r2s, cps, broi, income, bprofit, c2i, cr2i, execute=True)

    async def update_metrics_rk_stat(self, rk_id, i2r, cpi, cr2r, cpr, cr2d, r2s, cps, broi, income, bprofit, c2i, cr2i):
        sql = 'UPDATE rk_data SET i2r=$2, cpi=$3, cr2r=$4, cpr=$5, cr2d=$6, r2s=$7, cps=$8, broi=$9, income=$10, bprofit=$11, c2i=$12, cr2i=$13 WHERE rk_id=$1 returning *'
        return await self.execute(sql, rk_id, i2r, cpi, cr2r, cpr, cr2d, r2s, cps, broi, income, bprofit, c2i, cr2i, execute=True)

    async def update_acc_status_octo(self, upload_octo: bool, id_acc_bd: int, octo_uuid):
        sql = 'UPDATE accs_data SET upload_octo=$1, octo_acc_uuid=$3 WHERE id_acc_bd=$2 returning *'
        return await self.execute(sql, upload_octo, id_acc_bd, octo_uuid, execute=True)

    async def update_acc_fbtproxy_id(self, fbt_proxy_id: int, id_acc_bd: int):
        sql = 'UPDATE accs_data SET fbt_proxy_id=$1 WHERE id_acc_bd=$2 returning *'
        return await self.execute(sql, fbt_proxy_id, id_acc_bd, execute=True)

    async def update_status_octo_in_bd(self, id_acc_bd: int, upload_octo):
        sql = 'UPDATE accs_data SET upload_octo=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, upload_octo, fetchrow=True)

    async def update_status_fbt_in_bd(self, id_acc_bd: int, upload_fbtool):
        sql = 'UPDATE accs_data SET upload_fbtool=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, upload_fbtool, fetchrow=True)

    async def update_fbtvalue(self,id_acc_bd, upload_fbtool, fbt_proxy_id, fbt_acc_id, proxy_id):
        sql = 'UPDATE accs_data SET upload_fbtool=$2, fbt_proxy_id=$3, fbt_acc_id=$4, proxy_id=$5 WHERE id_acc_bd=$1'
        return await self.execute(sql, id_acc_bd, upload_fbtool, fbt_proxy_id, fbt_acc_id, proxy_id, execute=True)

    async def update_status_acc_fbt(self, id_acc_bd, fbt_status, comments):
        sql = "UPDATE accs_data SET fbt_status=$2, comments=$3 WHERE id_acc_bd=$1"
        return await self.execute(sql, id_acc_bd, fbt_status, comments, fetchrow=True)

    async def update_fbt_id_proxy(self, proxy_id: int, fbt_id: int):
        sql = 'UPDATE proxy_data SET fbt_id=$2 WHERE proxy_id=$1 returning *'
        return await self.execute(sql, proxy_id, fbt_id, fetchrow=True)

    async def update_acc_token(self, id_acc_bd: int, token):
        sql = 'UPDATE accs_data SET token=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, token, fetchrow=True)

    async def update_acc_vertical(self, id_acc_bd: int, vertical):
        sql = 'UPDATE accs_data SET vertical=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, vertical, fetchrow=True)

    async def update_acc_dop_comment(self, id_acc_bd: int, dop_comment):
        sql = 'UPDATE accs_data SET dop_comment=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, dop_comment, fetchrow=True)

    async def update_acc_password(self, id_acc_bd: int, psw):
        sql = 'UPDATE accs_data SET psw=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, psw, fetchrow=True)

    async def update_acc_2fa(self, id_acc_bd: int, f2a):
        sql = 'UPDATE accs_data SET f2a=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, f2a, fetchrow=True)

    async def update_acc_cards(self, id_acc_bd: int, cards):
        sql = 'UPDATE accs_data SET cards=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, cards, fetchrow=True)

    async def update_acc_comments(self, id_acc_bd: int, comments):
        sql = 'UPDATE accs_data SET comments=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, comments, fetchrow=True)

    async def update_acc_uniq_clicks_keitara(self, id_acc_bd: int, not_unic_clicks_in_keitaro):
        sql = 'UPDATE accs_data SET not_unic_clicks_in_keitaro=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, not_unic_clicks_in_keitaro, fetchrow=True)

    async def update_acc_spend_cards(self, id_acc_bd: int, spend_cards):
        sql = 'UPDATE accs_data SET spend_cards=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, spend_cards, fetchrow=True)

    async def update_acc_status(self, id_acc_bd: int, status):
        sql = 'UPDATE accs_data SET status=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, status, fetchrow=True)

    async def update_rk_data_kt_campaign_name(self, account_id, kt_campaign_name):
        sql = 'UPDATE rk_data SET kt_campaign_name=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, kt_campaign_name, fetchrow=True)

    async def update_ad_data_kt_campaign_name(self, account_id, kt_campaign_name):
        sql = 'UPDATE ad_data SET kt_campaign_name=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, kt_campaign_name, fetchrow=True)

    async def update_rk_data_kt_campaign_name2(self, account_id, kt_campaign_name):
        sql = 'UPDATE rk_data_daily SET kt_campaign_name=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, kt_campaign_name, fetchrow=True)

    async def update_ad_data_kt_campaign_name2(self, account_id, kt_campaign_name):
        sql = 'UPDATE ad_data_daily SET kt_campaign_name=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, kt_campaign_name, fetchrow=True)

    async def update_rk_data_kt_campaign_id(self, account_id, kt_campaign_id):
        sql = 'UPDATE rk_data SET kt_campaign_id=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, kt_campaign_id, fetchrow=True)

    async def update_ad_data_kt_campaign_id(self, account_id, kt_campaign_id):
        sql = 'UPDATE ad_data SET kt_campaign_id=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, kt_campaign_id, fetchrow=True)

    async def update_rk_data_kt_campaign_id2(self, account_id, kt_campaign_id):
        sql = 'UPDATE rk_data_daily SET kt_campaign_id=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, kt_campaign_id, fetchrow=True)

    async def update_ad_data_kt_campaign_id2(self, account_id, kt_campaign_id):
        sql = 'UPDATE ad_data_daily SET kt_campaign_id=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, kt_campaign_id, fetchrow=True)

    async def update_rk_data_creo_id(self, account_id, creo_id):
        sql = 'UPDATE rk_data SET creo_id=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, creo_id, fetchrow=True)

    async def update_ad_data_creo_id(self, account_id, creo_id):
        sql = 'UPDATE ad_data SET creo_id=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, creo_id, fetchrow=True)

    async def update_rk_data_creo_id2(self, account_id, creo_id):
        sql = 'UPDATE rk_data_daily SET creo_id=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, creo_id, fetchrow=True)

    async def update_ad_data_creo_id2(self, account_id, creo_id):
        sql = 'UPDATE ad_data_daily SET creo_id=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, creo_id, fetchrow=True)

    async def update_rk_data_install_or_dep(self, account_id, install_or_dep):
        sql = 'UPDATE rk_data SET install_or_dep=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, install_or_dep, fetchrow=True)

    async def update_ad_data_install_or_dep(self, account_id, install_or_dep):
        sql = 'UPDATE ad_data SET install_or_dep=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, install_or_dep, fetchrow=True)

    async def update_rk_data_install_or_dep2(self, account_id, install_or_dep):
        sql = 'UPDATE rk_data_daily SET install_or_dep=$2 WHERE rk_id=$1'
        return await self.execute(sql, account_id, install_or_dep, fetchrow=True)

    async def update_ad_data_install_or_dep2(self, account_id, install_or_dep):
        sql = 'UPDATE ad_data_daily SET install_or_dep=$2 WHERE ad_id=$1'
        return await self.execute(sql, account_id, install_or_dep, fetchrow=True)

    async def update_fbt_acc_id(self, id_acc_bd: int, fbt_acc_id: int):
        sql = 'UPDATE accs_data SET fbt_acc_id=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, fbt_acc_id, fetchrow=True)

    async def update_last_spend_update_time(self, id_acc_bd: int, last_spend_update_time: int):
        sql = 'UPDATE accs_data SET last_spend_update_time=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, last_spend_update_time, fetchrow=True)

    async def update_proxy_id_in_acc_table(self, id_acc_bd: int, proxy_id: int):
        sql = 'UPDATE accs_data SET proxy_id=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, proxy_id, fetchrow=True)

    async def update_acc_id_in_proxy_table(self, id_acc_bd: int, proxy_id: int):
        sql = 'UPDATE proxy_data SET accs=$1 WHERE proxy_id=$2 returning *'
        return await self.execute(sql, id_acc_bd, proxy_id, fetchrow=True)

    async def update_kt_cmpaign_id_in_acc_table(self, id_acc_bd: int, kt_campaign_id: int):
        sql = 'UPDATE accs_data SET kt_campaign_id=$2 WHERE id_acc_bd=$1 returning *'
        return await self.execute(sql, id_acc_bd, kt_campaign_id, fetchrow=True)

    async def delete_proxy_bd(self, ip: str):
        sql = 'DELETE FROM proxy_data WHERE ip=$1'
        return await self.execute(sql, ip, execute=True)

#-------------------------------------------------------------------------------------------------

    async def delete_web_from_bd(self, id: int):
        sql = 'DELETE FROM web_data WHERE affise_id=$1'
        return await self.execute(sql, id, execute=True)



    async def get_all_webs(self):
        sql = "SELECT * FROM web_data"
        return await self.execute(sql, fetch=True)
