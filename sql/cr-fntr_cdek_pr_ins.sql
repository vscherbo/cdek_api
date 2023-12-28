-- DROP FUNCTION shp.fntr_cdek_pr_ins();

CREATE OR REPLACE FUNCTION shp.fntr_cdek_pr_ins()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
declare 
loc_res varchar;
loc_shp_id varchar;
/*
	ret varchar;
	cdek_num varchar; 
	sts int;
	mail_body varchar default 'error';
*/
BEGIN

-- 10 - успешно запросили, 20 - скачали, 90 - ошибка
loc_res := shp.cdek_download_barcode(NEW.order_uuid);
if loc_res = '' then
    -- Ok
    UPDATE shp.cdek_preorder_params SET dl_status = 20 WHERE barcode_uuid = NEW.order_uuid;
else
    -- Fail
    loc_res := format('Ошибка загрузки pdf: %s', loc_res);
    with updated as (
        UPDATE shp.cdek_preorder_params SET dl_status = 90 WHERE barcode_uuid = NEW.order_uuid
        RETURNING shp_id)
        SELECT shp_id::varchar FROM updated into loc_shp_id ;

    -- DEBUG: PERFORM send_noreply('vscherbo@kipspb.ru', format('СДЭК: %s', COALESCE(loc_shp_id, 'unknown')),
    -- PROD: 
    PERFORM send_noreply('cdek-fail@kipspb.ru', format('СДЭК: %s', COALESCE(loc_shp_id, 'unknown')),
        loc_res, 't');
end if;


/*
--ret=cdek_check_uuid(OLD.our_firm, OLD.cdek_uuid);
ret=cdek_check_uuid('api'::varchar, OLD.cdek_uuid::varchar);
select cdek_number, sts_code, ret_msg INTO cdek_num, sts, ret from cdek_preorder_params where shp_id=OLD.shp_id;
if cdek_num Is Not Null then
	mail_body='shp_id: ' || OLD.shp_id::varchar || ' фирма: ' || OLD.our_firm || ' cdek_number: ' || cdek_num;
--	PERFORM send_noreply('petrushenko@kipspb.ru', 'СДЭК', mail_body, 't');
	PERFORM send_noreply('machulin@kipspb.ru', 'СДЭК', mail_body, 't');
else
	PERFORM arc_energo.put_msg('pam_event','e' || OLD.shp_id::varchar) || ret;
	mail_body='shp_id: ' || OLD.shp_id::varchar || ' фирма: ' || OLD.our_firm || ' cdek_number: ' || ret;
--	PERFORM send_noreply('vscherbo@kipspb.ru', 'СДЭК', mail_body, 't');
	PERFORM send_noreply('machulin@kipspb.ru', 'СДЭК', mail_body, 't');
end if;
*/
RETURN NEW;
END;
$function$
;

