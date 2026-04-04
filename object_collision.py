import numpy as np
import math
import random

def handle_wall_collision(object, boundry, energy_loss, friction):

    if touching_boundry(object, boundry):

        collision_normal = snap_to_boundry(object, boundry)

        tangent = np.array([collision_normal[1], -collision_normal[0]])

        # project velocity onto normal and tangent to essentially get how
        # much of the velocity is going into the wall and along the wall
        velocity_along_normal = np.dot(object.velocity, collision_normal)
        velocity_along_tangent = np.dot(object.velocity, tangent)

        # only bounce if moving into boundry
        if velocity_along_normal < 0: 
            object.velocity = (velocity_along_tangent * tangent * friction) - (velocity_along_normal * collision_normal) * energy_loss

# collision with boundry(walls, floor, etc)
def touching_boundry(object, boundry):
    # get the closest point on the boundry to the center of the object, 
    # then check if that point is within the radius of the object
    point = np.array([object.x, object.y], dtype=float)
    closest = closest_point_on_boundry(point, boundry)
    offset = point - closest
    # squared distance
    dist_sq = np.dot(offset, offset)

    return dist_sq <= object.radius * object.radius

def closest_point_on_boundry(point, boundry):
    # Project point onto the boundry line, then clamp to the segment
    start = np.array(boundry.start, dtype=float)
    end = np.array(boundry.end, dtype=float)
    segment = end - start
    # squared length is faster to compute then square root
    seg_len_sq = np.dot(segment, segment)

    # boundry is single point
    if seg_len_sq == 0:
        return start

    # Clamp to [0, 1] so we test distance to the finite segment, not an infinite line.
    # t is the parameter that describes how far along the segment the closest point is.
    # explination of this dot product: project the vector from start to point onto the 
    # segment vector, then divide by the length of the segment to get a value between 0 and 1.
    # which can be viewed as percentage along the segment where the point is.
    t = np.dot(point - start, segment) / seg_len_sq
    # if 0, cloest is start, if 1, closest is end, if 0.5, closest is middle of the segment
    t = max(0.0, min(1.0, t))
    return start + t * segment
    
def snap_to_boundry(object, boundry):
    point = np.array([object.x, object.y])
    closest = closest_point_on_boundry(point, boundry)
    offset = point - closest
    # euclidean distance from object center to closest point on boundry
    distance = np.linalg.norm(offset)

    # obj directly on boundry
    if distance == 0:
        collision_normal = boundry.normal
    # normalize the offset to get the collision normal
    else:
        collision_normal = offset / distance

    correction = object.radius - distance
    if correction > 0:
        object.x += collision_normal[0] * correction
        object.y += collision_normal[1] * correction

    return collision_normal

def simulate_move(object, boundries, energy_loss, friction):
    
    for boundry in boundries:
        handle_wall_collision(object, boundry, energy_loss, friction)

    object.move()

def calculate_distance(object, object2):

    dx = object.x - object2.x
    dy = object.y - object2.y
    distance = math.sqrt(dx**2 + dy**2)
    return distance

# collision between two objects
def check_collision(object, object2):

    distance = calculate_distance(object, object2)

    if distance < object.radius + object2.radius:
        return True
    return False

def handle_object_collision(object1, object2, energy_loss, friction):

    if check_collision(object1, object2):

        distance = calculate_distance(object1, object2)

        # randomly seperate objects if they are inside of eachother
        if distance == 0:
            directions = [-1, 1]
            object1.x += object1.radius * 2 * random.choice(directions) + 1
            object1.y += object1.radius * 2 * random.choice(directions) + 1
            distance = calculate_distance(object1, object2)
        
        # Normal vector: from object1 toward object2
        normal = np.array([(object2.x - object1.x) / distance,
                           (object2.y - object1.y) / distance])
        # 90 degree rotation of normal
        tangent = np.array([-normal[1], normal[0]])
        
        # seperate objects that intersect
        overlap = (object1.radius + object2.radius) - distance

        if overlap > 0:
            m1 = object1.mass
            m2 = object2.mass
            total_mass = m1 + m2

            # Split the correction by inverse mass so lighter objects move more.
            object1_correction = overlap * (m2 / total_mass)
            object2_correction = overlap * (m1 / total_mass)

            object1.x -= normal[0] * object1_correction
            object1.y -= normal[1] * object1_correction
            object2.x += normal[0] * object2_correction
            object2.y += normal[1] * object2_correction

        # Relative velocity from object1 to object2.
        # Using v2 - v1 keeps the impulse sign convention correct.
        relative_velocity = object2.velocity - object1.velocity
        
        # Speed along the collision normal.
        relative_speed_along_normal = np.dot(relative_velocity, normal)
        relative_speed_along_tangent = np.dot(relative_velocity, tangent)

        # If relative speed along normal is very small, skip collision response to prevent jitter
        if abs(relative_speed_along_normal) <= 0.01:
            return

        # Objects are moving apart after penetration has already been resolved.
        if relative_speed_along_normal >= 0:
            return
        
        m1 = object1.mass
        m2 = object2.mass

        impulse_normal = (-(1 + energy_loss) * relative_speed_along_normal) / (1/m1 + 1/m2)

        # friction is used as a damping factor in the rest of the code (0.99 ~= low friction).
        # Convert to a Coulomb-style coefficient for contact impulses.
        friction_coeff = max(0.0, min(1.0, 1.0 - friction))

        # Clamp friction impulse so tangential velocity is reduced without reversing direction.
        impulse_tangent = max(-abs(impulse_normal) * friction_coeff, min(abs(impulse_normal) * friction_coeff, (-relative_speed_along_tangent) / (1/m1 + 1/m2)))

        # Apply impulse to the objects velocities
        # The impulse is applied in the direction of the normal vector, and scaled by the inverse of the mass to 
        # determine how much each object should be affected based on its mass.
        object1.velocity -= (impulse_normal * normal + impulse_tangent * tangent) / m1
        object2.velocity += (impulse_normal * normal + impulse_tangent * tangent) / m2