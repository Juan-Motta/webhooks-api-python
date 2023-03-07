from typing import Dict, List

from app.main import app

async def get_service_by_id(service_id: int) -> List[Dict]:
    query: str = f"""
    SELECT
        s.id                                                                                                AS "id",
        json_build_object(
            'id', u.id,
            'fist_name', u.first_name,
            'last_name', u.last_name,
            'nid', u.nid,
            'mobile_phone', u.mobile_phone
        )                                                                                                   AS "user",
        CASE
            WHEN w.id IS NOT NULL
            THEN json_build_object(
                'id', w.id,
                'user', json_build_object(
                    'id', wu.id,
                    'first_name', wu.first_name,
                    'last_name', wu.last_name,
                    'nid', wu.nid,
                    'mobile_phone', wu.mobile_phone
                ),
                'vehicle', json_build_object(
                    'id', wv.id,
                    'vehicle_type', json_build_object(
                        'id', wvt.id,
                        'name', wvt.name
                    ),
                    'car_plate', wv.car_plate
                )
            )
        END                                                                                                 AS "worker",
        CASE
            WHEN co.id IS NOT NULL
            THEN json_build_object(
                'id', co.id,
                'company_name', co.company_name,
                'legal_name', co.legal_name,
                'nid_company', co.nid_company,
                'contact_role', co.contact_role,
                'billing_address', co.billing_address,
                'billing_period', co.billing_period,
                'configurations', co.configurations,
                'enterprise', co.enterprise, 
                'cost_center', co.cost_center
            )
        END                                                                                                 AS company,
        (
            SELECT
                json_build_object(
                    'id', sst.id,
                    'name', sst.name,
                    'reason', json_build_object(
                        'id', srt.id,
                        'name', srt.name,
                        'description', ss.reason_description
                    ),
                    'mishap', json_build_object(
                        'id', smt.id,
                        'name', smt.name,
                        'description', ss.mishap_description
                    )
                )
            FROM services_states ss
            LEFT JOIN services_state_types sst ON ss.service_state_type_id = sst.id
            LEFT JOIN services_reason_types srt ON ss.reason_type_id = srt.id
            LEFT JOIN services_mishap_types smt ON ss.mishap_type_id = smt.id
            WHERE sst.id = (
                SELECT
                    max(sssq.service_state_type_id)
                FROM services_states sssq
                WHERE sssq.service_id = s.id
                AND sssq.active = True
                GROUP BY sssq.id
                ORDER BY sssq.id DESC
                LIMIT 1
            )
            AND ss.service_id = s.id
            AND ss.active = true
            ORDER BY ss.id DESC
            LIMIT 1
        )                                                                                                   AS "state",
        (
            SELECT json_agg(json_build_object(
                'id', ss.id,
                'name', ss.name,
                'latitude', ss.latitude,
                'longitude', ss.longitude,
                'order', ss."order",
                'address', ss.address,
                'description', ss.description,
                'worker_observation', ss.worker_observation,
                'city', ss.city,
                'city_id', ss.stop_city_id,
                'assistants', ss.assistants,
                'additional_data', ss.additional_data,
                'novelties', (
                    SELECT json_agg(json_build_object(
                        'id', n.id,
                        'name', nt.name,
                        'description', n.description)) AS json_agg
                    FROM novelties n
                    LEFT JOIN novelty_types nt ON n.novelty_type_id = nt.id
                    WHERE ss.id = n.stop_id),
                'stop_states', (
                    SELECT json_agg(json_build_object(
                        'id', sss.id,
                        'name', ssss.name,
                        'created_at', sss.created_at)) AS json_agg
                    FROM services_stop_states sss
                    LEFT JOIN services_stop_state_types ssss ON sss.stop_state_type_id = ssss.id
                    WHERE ss.id = sss.stop_id))) AS json_agg
            FROM services_stops ss
            WHERE ss.service_id = s.id
        )                                                                                                   AS stops,
        s.date_time AT TIME ZONE 'America/Bogota'                                                           AS "date_time",
        s.created_at AT TIME ZONE 'America/Bogota'                                                          AS "created_at",
        s.programmed                                                                                        AS "programmed",
        s.kms_amount                                                                                        AS "kms_amount",
        s.approx_duration                                                                                   AS "approx_duration",
        json_build_object(
                'id', spm.id,
                'name', spm.name
        )                                                                                                   AS "service_payment_type",
        s.active                                                                                            AS "active",
        json_build_object(
                'id', sc.id,
                'name', sc.name
        )                                                                                                   AS "city",
        json_build_object(
                'id', st.id,
                'name', st.name
        )                                                                                                   AS "service_type",
        json_build_object(
                'id', sm.id,
                'name', sm.name
        )                                                                                                   AS "modality",
        s.history_id                                                                                        AS "history_id",
        s.worker_money                                                                                      AS "worker_money",
        CASE
            WHEN sct.id IS NOT NULL
            THEN json_build_object(
                'id', sct.id,
                'name', sct.name
            )
        END                                                                                                 AS "cargo_type",
        CASE
            WHEN vt.id IS NOT NULL
            THEN json_build_object(
                'id', vt.id,
                'name', vt.name
            )
        END                                                                                                 AS "vehicle_type",
        json_build_object(
            'id', sl.id,
            'name', sl.name
        )                                                                                                   AS "service_line",
        COALESCE((sad.data -> 'gratification'::text)::numeric, 0::numeric)                                  AS "gratification",
        CAST(sad.data AS json)                                                                              AS "additional_data",
        COALESCE((
            SELECT
                sum(msbrd.base_rate_value) + COALESCE(sum(msard.additional_rate_value), 0::numeric) +
                COALESCE(sum(msrd.rate_value), 0::numeric)
            FROM money_movements mm
            JOIN money_movement_detail mmd ON mm.id = mmd.movement_id
            JOIN money_type_movements mtm ON mm.type_movement_id = mtm.id AND mtm.lifecycle_op = true
            LEFT JOIN money_service_base_rates_details msbrd ON mmd.user_base_rate_id = msbrd.id
            LEFT JOIN money_service_additional_rates_details msard
                    ON mmd.user_additional_rate_id = msard.id
            LEFT JOIN money_service_reference_details msrd ON mmd.money_service_reference_id = msrd.id
            WHERE mm.service_id = s.id
            GROUP BY mm.id
            ORDER BY mm.id DESC
            LIMIT 1), s.total_price
        )                                                                                                   AS "total_price"
    FROM services s
    LEFT JOIN services_payment_methods spm ON s.payment_method_id = spm.id
    LEFT JOIN services_cities sc ON s.city_id = sc.id
    LEFT JOIN services_modalities sm ON s.modality_id = sm.id
    LEFT JOIN services_types st ON s.service_type_id = st.id
    LEFT JOIN services_cargo_types sct ON s.cargo_type_id = sct.id
    LEFT JOIN vehicle_type vt ON s.vehicle_type_id = vt.id
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN workers w ON s.worker_id = w.id
    LEFT JOIN users wu ON w.users_id = wu.id
    LEFT JOIN vehicles wv ON w.id = wv.worker_id
    LEFT JOIN vehicle_type wvt ON wv.vehicle_type_id = wvt.id
    LEFT JOIN services_lines_service_types slst on st.id = slst.servicetype_id
    LEFT JOIN services_lines sl ON slst.servicelines_id = sl.id
    LEFT JOIN services_additional_data sad ON s.id = sad.service_id
    LEFT JOIN companies_branch_offices_user cbou ON u.id = cbou.user_id
    LEFT JOIN companies_branch_offices cbo ON cbou.branch_office_id = cbo.id
    LEFT JOIN companies co ON cbo.company_id = co.id
    WHERE
        s.id = {service_id} AND
        s.active = true
    LIMIT 1;
    """
    data = await app.state.service_db.execute(query)
    return data