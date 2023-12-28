-- shp.vw_cdek_to_atol исходный текст

CREATE OR REPLACE VIEW shp.vw_cdek_to_atol
AS SELECT prep.prep_id,
    cd.dt_insert,
    prep.bill_no,
    sb.shp_id
   FROM vw_rcpt_prepayed prep
     JOIN ship_bills sb ON prep.bill_no = sb.bill AND sb.shp_id IS NOT NULL
     JOIN cdek_preorder_params cpp ON cpp.shp_id = sb.shp_id
     JOIN cdek_order_status cd ON cd.order_uuid = cpp.cdek_uuid AND cd.code = 'DELIVERED'::character varying
  WHERE NOT (EXISTS ( SELECT 1
           FROM atol_rcpt_q
          WHERE prep.prep_id = atol_rcpt_q.ext_id));

-- Permissions

ALTER TABLE shp.vw_cdek_to_atol OWNER TO arc_energo;
GRANT ALL ON TABLE shp.vw_cdek_to_atol TO arc_energo;
