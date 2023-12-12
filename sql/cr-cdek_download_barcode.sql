-- DROP FUNCTION shp.cdek_download_barcode(varchar, uuid);
DROP FUNCTION shp.cdek_download_barcode(uuid, varchar);

CREATE OR REPLACE FUNCTION shp.cdek_download_barcode(
--    arg_firm varchar,
    arg_uuid uuid, -- barcode uuid
    arg_filename varchar DEFAULT NULL)
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/cdek_api';
  loc_filename VARCHAR;
  loc_firm VARCHAR;
BEGIN
IF arg_filename is NULL THEN
    SELECT cdek_number INTO loc_filename FROM shp.cdek_preorder_params WHERE
    cdek_number is not null
    AND barcode_uuid = arg_uuid;
    IF NOT FOUND OR loc_filename is NULL THEN
        loc_filename := arg_uuid;
    END IF;
ELSE
    loc_filename := arg_filename;
END IF;

SELECT our_firm INTO loc_firm FROM shp.cdek_preorder_params WHERE
cdek_number is not null
AND barcode_uuid = arg_uuid;
RAISE NOTICE 'loc_firm=%', loc_firm;
IF FOUND AND loc_firm is NOT NULL THEN
    cmd := format('%s/cdek_download_barcode.py --log_file=%s/cdek_download_barcode.log --conf=%s --uuid=%s --outpdf=%s', 
        wrk_dir, -- script dir
        format('%s/logs', wrk_dir), -- logfile dir
        format('%s/cdek_%s.conf', wrk_dir, loc_firm), -- conf file
        arg_uuid,
        format('%s/barcodes/%s.pdf', wrk_dir, loc_filename));

    IF cmd IS NULL 
    THEN 
       err_str := 'cdek_download_barcode cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd, wrk_dir) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE NOTICE 'cdek_download_barcode cmd=%^err_str=[%]', cmd, err_str; 
       ret_str := err_str;
    END IF;
ELSE 
    ret_str := format('Не найдена фирма-отправитель для uuid ШК=%s', arg_uuid);
END IF;

    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

