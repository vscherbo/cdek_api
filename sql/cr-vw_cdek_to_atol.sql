-- shp.vw_cdek_to_atol исходный текст

CREATE OR REPLACE VIEW shp.vw_cdek_to_atol
AS SELECT prep.prep_id,
    cd.dt_insert,
    prep.bill_no,
    sb.shp_id
   FROM vw_rcpt_prepayed prep
     JOIN "Счета" b ON b."№ счета" = prep.bill_no AND b."ДокТК" IS NOT NULL
     JOIN ship_bills sb ON prep.bill_no = sb.bill AND sb.shp_id IS NOT NULL
     JOIN cdek_order_status cd ON cd.cdek_number = b."ДокТК" AND cd.code = 'DELIVERED'::character varying;

-- Permissions

ALTER TABLE shp.vw_cdek_to_atol OWNER TO arc_energo;
GRANT ALL ON TABLE shp.vw_cdek_to_atol TO arc_energo;
