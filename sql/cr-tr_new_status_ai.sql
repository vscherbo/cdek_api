-- DROP FUNCTION shp.fntr_cdek_chg_status();

CREATE OR REPLACE FUNCTION shp.fntr_cdek_chg_status()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
declare 
loc_firm varchar;
ret varchar;
begin
    if new.code = 'CREATED' then -- предзаказ принят СДЭКом, запрашиваем статус по uuid
        select our_firm into loc_firm
        from shp.cdek_order_status
        where cdek_order_status = new.order_uuid;
       
        ret := shp.cdek_check_uuid(loc_firm, new.order_uuid); -- из триггера обращаться к сайту СДЭК нехорошо,
        -- лучше помещать uuid в таблицу "очередь для запроса статуса", а её обрабатывать скриптом по расписанию
        
        -- запрос ШК
    elseif new.code = 'RECEIVED_AT_SHIPMENT_WAREHOUSE' then -- послыка принята СДЭКом,
        -- для физиков нужен чек "полный расчёт"
    end if;

return new;
END;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_cdek_chg_status() OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.fntr_cdek_chg_status() TO public;
GRANT ALL ON FUNCTION shp.fntr_cdek_chg_status() TO arc_energo;

-- CREATE TRIGGER
/**
create trigger cdek_new_status_ai after insert on
shp.cdek_order_status for each row
when ((new.status_code = '3'::character varying)) execute procedure fntr_cdek_chg_status()
**/
