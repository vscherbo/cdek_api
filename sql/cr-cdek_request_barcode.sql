-- DROP FUNCTION shp.cdek_request_barcode(varchar, varchar);
--DROP FUNCTION shp.cdek_request_barcode(uuid);

CREATE OR REPLACE FUNCTION shp.cdek_request_barcode(
--  arg_firm varchar,
    arg_uuid uuid)
  RETURNS character varying -- new address_id OR some message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/cdek_api';
loc_firm varchar;
BEGIN

SELECT our_firm INTO loc_firm FROM shp.cdek_preorder_params
WHERE 
cdek_number IS NOT NULL
AND cdek_uuid = arg_uuid;
RAISE NOTICE 'shp.cdek_request_barcode: loc_firm=%, arg_uuid=%', loc_firm, arg_uuid;
IF FOUND AND loc_firm is NOT NULL THEN
    cmd := format('%s/cdek_request_barcode.py --log_file=%s/cdek_request_barcode.log --conf=%s --uuid=%s', 
        wrk_dir, -- script dir
        format('%s/logs', wrk_dir), -- logfile dir
        format('%s/cdek_%s.conf', wrk_dir, loc_firm), -- conf file
        arg_uuid);

    IF cmd IS NULL THEN 
       err_str := 'cdek_request_barcode cmd IS NULL';
       -- RAISE NOTICE '%', err_str ;
        cmd := 'pwd';
    END IF;

    SELECT * FROM public.exec_shell(cmd, wrk_dir) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL THEN 
       --RAISE NOTICE 'cdek_request_barcode cmd=%^err_str=[%]', cmd, err_str;
       err_str := format('cdek_request_barcode cmd=%s^err_str=[%s]', cmd, err_str);
       -- ret_str := err_str;
    END IF;
ELSE
    err_str := format('Для заказа ШК %s не найдена фирма-отправитель', arg_uuid);
END IF; 
    
IF err_str IS NOT NULL THEN 
   RAISE NOTICE '%', err_str;
   ret_str := err_str;
ELSE
    UPDATE shp.cdek_preorder_params SET dl_status = 10 WHERE cdek_uuid = arg_uuid;
END IF;
    
return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

