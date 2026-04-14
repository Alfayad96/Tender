from dataclasses import dataclass, asdict


@dataclass
class Tender:
    veroeffentlichung: str | None = None
    frist: str | None = None
    titel: str | None = None
    vergabeart: str | None = None
    auftraggeber: str | None = None
    detail_url: str | None = None

    ausschreibungs_id: str | None = None
    auftraggeber_detail: str | None = None
    abgabefrist_detail: str | None = None
    auftragsgegenstand_detail: str | None = None

    vergabeordnung: str | None = None
    vergabeart_detail: str | None = None
    status_detail: str | None = None
    frist_aufklaerungsfragen: str | None = None
    teilnahmefrist: str | None = None
    auftraggeber_name: str | None = None

    final_detail_url: str | None = None
    verfahrensangaben_url: str | None = None
    final_verfahrensangaben_url: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)