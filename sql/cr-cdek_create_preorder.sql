CREATE OR REPLACE FUNCTION shp.cdek_create_preorder(
    arg_firm varchar,
    arg_shp_id integer)
  RETURNS character varying
AS
$BODY$
DECLARE cmd character varying;
  ret_str VARCHAR := '';
  err_str VARCHAR := '';
  wrk_dir text := '/opt/cdek_api';
BEGIN
    -- cmd := format('~/.pyenv/shims/python %s/cdek_create_preorder.py --log_file=%s/cdek_create_preorder.log --conf=%s --shp=%s', 
    cmd := format('%s/cdek_create_preorder.py --log_file=%s/cdek_create_preorder.log --conf=%s --firm=%s --shp=%s', 
        wrk_dir, -- script dir
        format('%s/logs', wrk_dir), -- logfile dir
        format('%s/cdek_%s.conf', wrk_dir, arg_firm), -- conf file
        arg_firm,
        arg_shp_id);

    IF cmd IS NULL 
    THEN 
       err_str := 'cdek_create_preorder cmd IS NULL';
       RAISE '%', err_str ; 
    END IF;

    SELECT * FROM public.exec_shell(cmd, wrk_dir) INTO ret_str, err_str ;
    
    IF err_str IS NOT NULL
    THEN 
       RAISE NOTICE 'cdek_create_preorder cmd=%^err_str=[%]', cmd, err_str; 
       ret_str := err_str;
    ELSE
       ret_str := '';  -- empty string instead of UUID if OK
    END IF;
    
    return ret_str;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

