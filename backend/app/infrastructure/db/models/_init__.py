"""ORM models for persistence. One file per aggregate root.

Models mirror the domain entities but are intentionally *separate* classes:
the domain layer stays free of SQLAlchemy so it can be unit-tested and
reasoned about without a database. Mapping between the two happens in the
repository implementations.
"""

from app.infrastructure.db.models.allotment import AllotmentModel
from app.infrastructure.db.models.candidate import CandidateModel
from app.infrastructure.db.models.category import CategoryModel
from app.infrastructure.db.models.college import CollegeModel
from app.infrastructure.db.models.course import CourseModel
from app.infrastructure.db.models.data_source import DataSourceModel
from app.infrastructure.db.models.district import DistrictModel
from app.infrastructure.db.models.etl_error import ETLErrorModel
from app.infrastructure.db.models.etl_run import ETLRunModel
from app.infrastructure.db.models.feature_flag import FeatureFlagModel
from app.infrastructure.db.models.fee import FeeModel
from app.infrastructure.db.models.historical_cutoff import HistoricalCutoffModel
from app.infrastructure.db.models.log import LogModel
from app.infrastructure.db.models.model_version import ModelVersionModel
from app.infrastructure.db.models.prediction import PredictionModel
from app.infrastructure.db.models.prediction_history import PredictionHistoryModel
from app.infrastructure.db.models.quota import QuotaModel
from app.infrastructure.db.models.recommendation import RecommendationModel
from app.infrastructure.db.models.round import RoundModel
from app.infrastructure.db.models.seat_matrix import SeatMatrixModel
from app.infrastructure.db.models.source_file import SourceFileModel
from app.infrastructure.db.models.state import StateModel
from app.infrastructure.db.models.system_setting import SystemSettingModel
from app.infrastructure.db.models.upload import UploadModel
from app.infrastructure.db.models.user import UserModel

__all__ = [
    "AllotmentModel",
    "CandidateModel",
    "CategoryModel",
    "CollegeModel",
    "CourseModel",
    "DataSourceModel",
    "DistrictModel",
    "ETLErrorModel",
    "ETLRunModel",
    "FeatureFlagModel",
    "FeeModel",
    "HistoricalCutoffModel",
    "LogModel",
    "ModelVersionModel",
    "PredictionHistoryModel",
    "PredictionModel",
    "QuotaModel",
    "RecommendationModel",
    "RoundModel",
    "SeatMatrixModel",
    "SourceFileModel",
    "StateModel",
    "SystemSettingModel",
    "UploadModel",
    "UserModel",
]
