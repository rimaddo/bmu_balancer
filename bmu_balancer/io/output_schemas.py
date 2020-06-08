from bmu_balancer.io.utils import PostLoadObjMixin
from bmu_balancer.models.engine import Solution


class SolutionSchema(PostLoadObjMixin):

    __model__ = Solution
