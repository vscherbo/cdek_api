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
        -- лучше помещать uuid в таблицу "очередь для запроса статуса" и отправлять сигнал в некий listener
        -- для обращения к сайту

        
        -- запрос ШК
    elseif new.code = 'RECEIVED_AT_SHIPMENT_WAREHOUSE' then -- послыка принята СДЭКом,
        -- заполнить в shp.shipment carr_doc, carr_docdt
        with orig_shp as (select shp_id from cdek_preorder_params cpp where NEW.order_uuid = cdek_uuid)
               update shp.shipments
               set carr_doc = NEW.cdek_number, carr_docdt = NEW.dt_insert --или NEW.date_time + 3!!!
               where shp_id = (select shp_id from orig_shp);
    end if;

return new;
END;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_cdek_chg_status() OWNER TO arc_energo;
