#include <pybind11/pybind11.h>
#include <cmath>
#include <algorithm>
#include <tuple>
#include <random>
#include <iostream>

namespace py = pybind11;

static std::tuple<bool, double, double, double, double, double, double, double, double>
resolve_object_collision(
    double x1, double y1,
    double vx1, double vy1,
    double m1, double r1,
    double x2, double y2,
    double vx2, double vy2,
    double m2, double r2,
    double energy_loss,
    double friction
) {

    std::random_device rd;
    std::mt19937 gen(rd());
    std::vector<int> random_values = {1, -1};
    std::uniform_int_distribution<> distrib(0, random_values.size() - 1);

    const double dx = x1 - x2;
    const double dy = y1 - y2;
    const double distance_sq = dx * dx + dy * dy;
    const double radius_sum = r1 + r2;
    const double radius_sum_sq = radius_sum * radius_sum;

    if (distance_sq >= radius_sum_sq) {
        return std::make_tuple(false, x1, y1, vx1, vy1, x2, y2, vx2, vy2);
    }

    double distance = std::sqrt(distance_sq);

    if (distance == 0.0) {
        // deterministic tiny offset to avoid division by zero when perfectly overlapped
        x1 += (r1 * 2.0) * random_values[distrib(gen)] + 1.0;
        y1 += (r1 * 2.0) * random_values[distrib(gen)] + 1.0;

        const double ndx = x1 - x2;
        const double ndy = y1 - y2;
        const double ndsq = ndx * ndx + ndy * ndy;
        distance = std::sqrt(ndsq);

        if (distance == 0.0) {
            return std::make_tuple(false, x1, y1, vx1, vy1, x2, y2, vx2, vy2);
        }
    }

    const double normal_x = (x2 - x1) / distance;
    const double normal_y = (y2 - y1) / distance;

    const double tangent_x = -normal_y;
    const double tangent_y = normal_x;

    const double overlap = radius_sum - distance;

    if (overlap > 0.0) {
        const double total_mass = m1 + m2;
        const double object1_correction = overlap * (m2 / total_mass);
        const double object2_correction = overlap * (m1 / total_mass);

        x1 -= normal_x * object1_correction;
        y1 -= normal_y * object1_correction;
        x2 += normal_x * object2_correction;
        y2 += normal_y * object2_correction;
    }

    const double relative_velocity_x = vx2 - vx1;
    const double relative_velocity_y = vy2 - vy1;

    const double relative_speed_along_normal =
        relative_velocity_x * normal_x + relative_velocity_y * normal_y;
    const double relative_speed_along_tangent =
        relative_velocity_x * tangent_x + relative_velocity_y * tangent_y;

    if (std::abs(relative_speed_along_normal) <= 0.01) {
        return std::make_tuple(true, x1, y1, vx1, vy1, x2, y2, vx2, vy2);
    }

    if (relative_speed_along_normal >= 0.0) {
        return std::make_tuple(true, x1, y1, vx1, vy1, x2, y2, vx2, vy2);
    }

    const double impulse_normal = (-(1.0 + energy_loss) * relative_speed_along_normal) /
                                  ((1.0 / m1) + (1.0 / m2));

    const double friction_coeff = std::clamp(1.0 - friction, 0.0, 1.0);

    const double tangent_impulse_ideal = (-relative_speed_along_tangent) / ((1.0 / m1) + (1.0 / m2));
    const double max_friction = std::abs(impulse_normal) * friction_coeff;
    const double impulse_tangent = std::clamp(tangent_impulse_ideal, -max_friction, max_friction);

    const double impulse_x = impulse_normal * normal_x + impulse_tangent * tangent_x;
    const double impulse_y = impulse_normal * normal_y + impulse_tangent * tangent_y;

    vx1 -= impulse_x / m1;
    vy1 -= impulse_y / m1;
    vx2 += impulse_x / m2;
    vy2 += impulse_y / m2;

    return std::make_tuple(true, x1, y1, vx1, vy1, x2, y2, vx2, vy2);
}

PYBIND11_MODULE(collision_core, m) {
    m.doc() = "C++ collision response kernel for pairwise circle collisions";
    m.def("resolve_object_collision", &resolve_object_collision,
          "Resolve one circle-circle collision and return updated state");
}
