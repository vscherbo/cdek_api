DROP FUNCTION shp.cdek_check_uuid(varchar, varchar);

CREATE OR REPLACE FUNCTION shp.cdek_check_uuid(
    arg_firm varchar,
    arg_uuid varchar)
  RETURNS character varying -- new address_id OR some message
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/cdek_api';
BEGIN
    IF arg_firm IS NULL THEN
        return 'Входной параметр arg_firm IS NULL';
    END IF;
    IF arg_firm = '' THEN
        return 'Входной параметр arg_firm пустая строка';
    END IF;

    cmd := format('%s/cdek_check_uuid.py --log_file=%s/cdek_check_uuid.log --conf=%s --uuid=%s', 
        wrk_dir, -- script dir
        format('%s/logs', wrk_dir), -- logfile dir
        format('%s/cdek_%s.conf', wrk_dir, arg_firm), -- conf file
        arg_uuid);

    IF cmd IS NULL 
    THEN 
       err_str := 'cdek_check_uuid cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd, wrk_dir) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE NOTICE 'cdek_check_uuid cmd=%^err_str=[%]', cmd, err_str; 
       ret_str := err_str;
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

