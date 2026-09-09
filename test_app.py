"""
Script de verificación y pruebas unitarias automáticas para el MVP.
Valida conexión, consultas SQL, filtros, KPIs y política estricta de privacidad.
"""

import unittest
import bcrypt
import yaml
from yaml.loader import SafeLoader
import db
import queries


class TestDashboardMatriculas(unittest.TestCase):

    def test_01_credentials_and_bcrypt(self):
        """Verifica que el archivo credentials.yaml sea válido y los hashes funcionen."""
        with open("credentials.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.load(f, Loader=SafeLoader)

        self.assertIn("credentials", cfg)
        self.assertIn("usernames", cfg["credentials"])
        users = cfg["credentials"]["usernames"]
        
        # Probar usuarios autorizados vigentes
        self.assertIn("jflores", users)
        jflores_hash = users["jflores"]["password"].encode("utf-8")
        self.assertTrue(bcrypt.checkpw("dire2690".encode("utf-8"), jflores_hash))

        self.assertIn("jcubas", users)
        jcubas_hash = users["jcubas"]["password"].encode("utf-8")
        self.assertTrue(bcrypt.checkpw("INFOJC18".encode("utf-8"), jcubas_hash))

        # Verificar que los usuarios eliminados no existan
        self.assertNotIn("admin", users)
        self.assertNotIn("jperez", users)
        self.assertNotIn("directivo", users)

    def test_02_database_engine(self):
        """Verifica que el engine de base de datos se inicialice correctamente."""
        engine, is_demo, status = db.get_db_engine()
        self.assertIsNotNone(engine)
        self.assertIsInstance(is_demo, bool)
        self.assertIsInstance(status, str)

    def test_03_filter_options(self):
        """Verifica la carga de opciones para los filtros de la barra lateral."""
        filters = queries.get_distinct_filter_values()
        self.assertIn("ciclos", filters)
        self.assertIn("locales", filters)
        self.assertIn("turnos", filters)
        self.assertIn("areas", filters)
        self.assertGreater(len(filters["ciclos"]), 0)
        self.assertGreater(len(filters["locales"]), 0)
        self.assertGreater(len(filters["turnos"]), 0)
        self.assertGreater(len(filters["areas"]), 0)

    def test_04_kpis(self):
        """Verifica que el cálculo de KPIs devuelva los 4 indicadores requeridos."""
        kpis = queries.get_kpis({})
        self.assertIn("total_matriculados", kpis)
        self.assertIn("locales_activos", kpis)
        self.assertIn("carreras_activas", kpis)
        self.assertIn("matriculados_hoy", kpis)
        self.assertGreater(kpis["total_matriculados"], 0)
        self.assertGreater(kpis["locales_activos"], 0)
        self.assertGreater(kpis["carreras_activas"], 0)

    def test_05_kpis_with_filters(self):
        """Verifica que los KPIs respondan a filtros aplicados."""
        all_filters = queries.get_distinct_filter_values()
        primer_ciclo = all_filters["ciclos"][:1]
        
        kpis_filtered = queries.get_kpis({"ciclos": primer_ciclo})
        kpis_total = queries.get_kpis({})
        
        self.assertLessEqual(kpis_filtered["total_matriculados"], kpis_total["total_matriculados"])

    def test_06_visualizations_data(self):
        """Verifica que todas las consultas de gráficos devuelvan DataFrames con datos y columnas esperadas."""
        empty_filters = {}

        df_ciclo = queries.get_matriculados_por_ciclo(empty_filters)
        self.assertFalse(df_ciclo.empty)
        self.assertListEqual(list(df_ciclo.columns), ["CICLO", "total"])

        df_local = queries.get_matriculados_por_local(empty_filters)
        self.assertFalse(df_local.empty)
        self.assertListEqual(list(df_local.columns), ["LOCAL", "total"])

        df_turno = queries.get_matriculados_por_turno(empty_filters)
        self.assertFalse(df_turno.empty)
        self.assertListEqual(list(df_turno.columns), ["TURNO", "total"])

        df_area = queries.get_matriculados_por_area(empty_filters)
        self.assertFalse(df_area.empty)
        self.assertListEqual(list(df_area.columns), ["AREA", "total"])

        df_carreras = queries.get_top_carreras(empty_filters, limit=15)
        self.assertFalse(df_carreras.empty)
        self.assertLessEqual(len(df_carreras), 15)
        self.assertListEqual(list(df_carreras.columns), ["CARRERA", "total"])

        df_evolucion = queries.get_evolucion_temporal(empty_filters)
        self.assertFalse(df_evolucion.empty)
        self.assertIn("fecha_matricula", df_evolucion.columns)
        self.assertIn("total", df_evolucion.columns)
        self.assertIn("total_acumulado", df_evolucion.columns)

        df_cruce = queries.get_cruce_local_turno(empty_filters)
        self.assertFalse(df_cruce.empty)
        self.assertListEqual(list(df_cruce.columns), ["LOCAL", "TURNO", "total"])

        df_resumen = queries.get_resumen_ciclo_local_turno(empty_filters)
        self.assertFalse(df_resumen.empty)
        self.assertListEqual(list(df_resumen.columns), ["CICLO", "LOCAL", "TURNO", "MATRICULADOS"])
        self.assertGreater(df_resumen["MATRICULADOS"].sum(), 0)

    def test_07_privacy_compliance(self):
        """Verifica estrictamente que ninguna consulta exponga datos personales."""
        forbidden_columns = {"APE_PATERNO", "APE_MATERNO", "NOMBRES", "CODIGO"}
        empty_filters = {}

        for func in [
            queries.get_matriculados_por_ciclo,
            queries.get_matriculados_por_local,
            queries.get_matriculados_por_turno,
            queries.get_matriculados_por_area,
            lambda f: queries.get_top_carreras(f, 15),
            queries.get_evolucion_temporal,
            queries.get_cruce_local_turno,
            queries.get_resumen_ciclo_local_turno,
        ]:
            df = func(empty_filters)
            cols = set(df.columns)
            intersection = cols.intersection(forbidden_columns)
            self.assertEqual(
                len(intersection), 0,
                f"Violación de privacidad detectada: {intersection} en {cols}"
            )

    def test_08_pagos_pendientes(self):
        """Verifica que el cálculo de pagos por matricular funcione y respete filtros de ciclo."""
        pagos_all = queries.get_pagos_pendientes({})
        self.assertIn("total_pagos", pagos_all)
        self.assertIn("total_monto", pagos_all)
        self.assertGreaterEqual(pagos_all["total_pagos"], 0)
        self.assertGreaterEqual(pagos_all["total_monto"], 0.0)

        # Probar con filtro por ciclo ORD_2026_II
        pagos_ord = queries.get_pagos_pendientes({"ciclos": ["ORD_2026_II"]})
        self.assertIn("total_pagos", pagos_ord)
        self.assertIn("total_monto", pagos_ord)
        self.assertLessEqual(pagos_ord["total_pagos"], pagos_all["total_pagos"])


if __name__ == "__main__":
    unittest.main()

