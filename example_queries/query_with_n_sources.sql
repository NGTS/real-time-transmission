select mjd, median_flux_offset, ref_image_id, n_sources
from transmission_log as l
join raw_image_list as r using (image_id)
join autoguider_refimage as i using (field, camera_id)
join (
    select ref_image_id, count(*) as n_sources from transmission_sources
    group by ref_image_id
) as s using (ref_image_id)
;


