from models import LostReport, FoundReport

class CandidateSelector:
    """
    Retrieves candidate reports for matching based on status, category, date windows, and filters.
    """

    @staticmethod
    def get_found_candidates_for_lost(lost_report: LostReport) -> list[FoundReport]:
        """
        Fetches active FoundReports that are potential candidates for a given LostReport.
        Applies preliminary filtering (ACTIVE status, user ownership check).
        """
        query = FoundReport.query.filter(
            FoundReport.status == 'ACTIVE',
            FoundReport.user_id != lost_report.user_id  # User shouldn't match against their own report
        )
        return query.all()

    @staticmethod
    def get_lost_candidates_for_found(found_report: FoundReport) -> list[LostReport]:
        """
        Fetches active LostReports that are potential candidates for a given FoundReport.
        """
        query = LostReport.query.filter(
            LostReport.status == 'ACTIVE',
            LostReport.user_id != found_report.user_id
        )
        return query.all()
