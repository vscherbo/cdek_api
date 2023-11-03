DROP FUNCTION shp.cdek_sender_phones(integer);

CREATE OR REPLACE FUNCTION shp.cdek_sender_phones(shpid integer)
 RETURNS TABLE(number character varying, additional character varying)
 LANGUAGE plpgsql
AS $function$
DECLARE
ret_ph varchar;

begin
if shpid <= 0 then
    return query
    select * from shp.stub_cdek_sender_phones(shpid);
else -- prod
    SELECT DISTINCT Фирма.Ф_Телефон INTO ret_ph
    FROM (ship_bills INNER JOIN Счета ON ship_bills.bill = Счета."№ счета") INNER JOIN Фирма ON Счета.фирма = Фирма.КлючФирмы
    WHERE ship_bills.shp_id=shpid;
    ret_ph='+7' || replace(ret_ph,' ','');
    ret_ph=replace(ret_ph,'(','');
    ret_ph=replace(ret_ph,')','');
    ret_ph=replace(ret_ph,'-','');

    return query 
    VALUES(ret_ph::varchar, ''::varchar);
end if; -- prod

end;
$function$
;

