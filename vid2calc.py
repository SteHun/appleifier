import cv2
import tqdm
import copy

NEWFRAME_VALUE = 50
TARGET_FPS = 10
TARGET_SIZE = (26, 9)

RED_WEIGHT = 1
GREEN_WEIGHT = 1
BLUE_WEIGHT = 1
THRESHOLD = 0.5


def get_white_or_black(matrix, x, y, pixel_width, pixel_height):
    matrix_to_scan = matrix[
                     round(y * pixel_height):round(y * pixel_height + pixel_height),
                     round(x * pixel_width):round(x * pixel_width + pixel_width)]
    brightness_value = [0, 0, 0]
    max_brightness = [0, 0, 0]
    for row in matrix_to_scan:
        for item in row:
            brightness_value[0] += item[0]
            brightness_value[1] += item[1]
            brightness_value[2] += item[2]
            max_brightness[0] += 255
            max_brightness[1] += 255
            max_brightness[2] += 255
    if brightness_value != [0, 0, 0]:
        pass
    brightness_value[0] = brightness_value[0] * RED_WEIGHT
    brightness_value[1] = brightness_value[1] * GREEN_WEIGHT
    brightness_value[2] = brightness_value[2] * BLUE_WEIGHT
    max_brightness[0] = max_brightness[0] * RED_WEIGHT
    max_brightness[1] = max_brightness[1] * GREEN_WEIGHT
    max_brightness[2] = max_brightness[2] * BLUE_WEIGHT

    min_white_value = sum(max_brightness) * THRESHOLD
    return sum(brightness_value) >= min_white_value


def matrix2string(matrix):
    return_string = ""
    for row in matrix:
        for item in row:
            return_string += '#' if item else ' '
        return_string += '\n'
    return_string += "--------------------------"
    return return_string


def convert(path, target_framerate):
    return_list = []
    buffer = [[False] * TARGET_SIZE[0] for _ in range(TARGET_SIZE[1])]

    target_frame_duration = 1 / target_framerate

    vid = cv2.VideoCapture(path)
    framerate = vid.get(cv2.CAP_PROP_FPS)
    frame_duration = 1 / framerate

    number_of_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_recorded = 0
    # for frame_number in range(number_of_frames):
    for frame_number in tqdm.tqdm(range(number_of_frames)):
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        success, image = vid.read()
        if not success:
            print("error???")
            break

        if frame_number * frame_duration >= frames_recorded * target_frame_duration:
            height, width, _ = image.shape
            pixel_width, pixel_height = width / TARGET_SIZE[0], height / TARGET_SIZE[1]
            old_buffer = copy.deepcopy(buffer)
            for row in range(TARGET_SIZE[1]):
                for item in range(TARGET_SIZE[0]):
                    buffer[row][item] = get_white_or_black(image, item, row, pixel_width, pixel_height)
                    if buffer[row][item] != old_buffer[row][item]:
                        return_list.append(item)
                        return_list.append(row)
            # print(frame_number)
            # print(matrix2string(buffer))

            return_list.append(NEWFRAME_VALUE)
            frames_recorded += 1
    vid.release()
    return return_list


def list2str(inlist):
    return str(inlist).replace('[', '{').replace(']', '}')


if __name__ == "__main__":
    out = convert("vid.mp4", 10)

    with open("out.txt", 'w') as file:
        file.write(list2str(out))
