def binary_search_circles(circle_list, target_x):
    left, right = 0, len(circle_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if circle_list[mid].x < target_x:
            left = mid + 1
        elif circle_list[mid].x > target_x:
            right = mid - 1
        else:
            return mid
    
    if left != target_x:
        return None

    return left

# function to find all circles within 2r of a given circle x coordinate
def find_near_circles(circle_index, circle_list):

    target_circle = circle_list[circle_index]
    near_circles = []

    if circle_index is None:
        return near_circles

    target_x = target_circle.x
    target_r = target_circle.r

    # check left side
    i = circle_index - 1
    while i >= 0 and abs(circle_list[i].x - target_x) <= 2 * target_r:
        near_circles.append(circle_list[i])
        i -= 1

    # check right side
    i = circle_index + 1
    while i < len(circle_list) and abs(circle_list[i].x - target_x) <= 2 * target_r:
        near_circles.append(circle_list[i])
        i += 1

    return near_circles
