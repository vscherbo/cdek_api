DROP FUNCTION shp.cdek_recipient(integer);

CREATE OR REPLACE FUNCTION shp.cdek_recipient(shpid integer, OUT company character varying, OUT name character varying, OUT passport_series character varying, OUT passport_number character varying, OUT passport_date_of_issue date, OUT passport_organization character varying, OUT email character varying, OUT inn character varying)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    xiva_d varchar;
begin
if shpid <= 0 then -- DEBUG
    select * into company, "name", passport_series, passport_number, passport_date_of_issue, passport_organization, email, inn
    from shp.stub_cdek_recipient(shpid);
else -- prod
    SELECT DISTINCT c.ЮрНазвание, e.ФИО, e.ЕАдрес, c.ИНН, d.xiva
    INTO company, "name", email, inn, xiva_d
    FROM ((ship_phones AS p 
    JOIN (delivery AS d 
    JOIN ship_bills AS b ON d.dlvr_id = b.dlvrid) ON p.dlvr_id = d.dlvr_id) 
    LEFT JOIN Работники AS e ON p.emp_code = e.КодРаботника) 
    LEFT JOIN Предприятия AS c ON e.Код = c.Код
    WHERE b.shp_id=shpid;

    if xiva_d Is Not Null then
        passport_series=left(xiva_d,4);
        passport_number=substr(xiva_d,6,6);
        if length(xiva_d)>20  then
            passport_date_of_issue=ret_date(substr(xiva_d,19,10));
            passport_organization=substr(xiva_d,30);
        end if;
    end if;
    if company Is Null then
        SELECT en.ЮрНазвание, em.ФИО, em.ЕАдрес, en.ИНН
        INTO company, "name", email, inn
        FROM ((Предприятия AS en 
        LEFT JOIN Работники AS em ON en.Код = em.Код) 
        JOIN (consignee AS c 
        JOIN delivery AS d ON c.csn_id = d.csn_id) ON en.Код = c.kod) 
        JOIN ship_bills AS b ON d.dlvr_id = b.dlvrid
        WHERE b.shp_id=shpid AND em.Дата<=b.credate 
        ORDER BY em.Дата DESC LIMIT 1;
    end if;
end if; -- prod

end;
$function$
;

