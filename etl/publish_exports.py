"""Export joined mart tables to CSV."""
from pathlib import Path
import pandas as pd
from config import get_connection, load_settings

def export_table(query: str, out_path: Path) -> int:
    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return len(df)

def main():
    settings = load_settings()
    out_dir = Path(settings.export_dir)
    rows = export_table("select * from mart.poles_fire_risk", out_dir / "poles_fire_risk.csv")
    print(f"Exported {rows} rows to {out_dir / 'poles_fire_risk.csv'}")

if __name__ == "__main__":  # pragma: no cover
    main()
