from support_Functions import convertPixelsToWhite, getShapeInfo, getCornersOfDrawingFrame, getCalcOfMaxMinValuesOfPixelHolder, getDistances
import numpy as np
import copy, random, math, cv2

samples_list = []
shape_list = []


# returns a new image_array which contains the modification in terms
# of translation
def getTranslationOfImage(image_array):
    print('===> TRANSLATION <===')

    cols, rows = getShapeInfo(image_array)

    new_distances = getDistances(
        getCalcOfMaxMinValuesOfPixelHolder(image_array), image_array)
    d_bb, d_rb, d_tb, d_lb = new_distances

    trans_m_options = random.randint(0, 3)

    y_value = 0
    x_value = 0

    ####===> to bottom and POSSIBLY to right OR left <===####
    if (trans_m_options == 0):
        if (d_bb > 1):
            y_value = random.randint(1, d_bb)
            x_value = 0

            bb_add_options = random.randint(0, 2)
            if (bb_add_options == 0 and d_rb > 1):
                x_value = random.randint(1, d_rb)
            elif (bb_add_options == 1 and d_lb > 1):
                x_value = random.randint(1, d_lb) * (-1)
        else:
            y_value = 0

            bb_add_options = random.randint(0, 2)
            if (bb_add_options == 0 and d_rb > 1):
                x_value = random.randint(1, d_rb)
            elif (bb_add_options == 1 and d_lb > 1):
                x_value = random.randint(1, d_lb) * (-1)
    ####===> to top and POSSIBLY to right OR left <===####
    elif (trans_m_options == 1):
        if (d_tb > 1):
            y_value = random.randint(1, d_tb) * (-1)
            x_value = 0

            tb_add_options = random.randint(0, 2)
            if (tb_add_options == 0 and d_rb > 1):
                x_value = random.randint(1, d_rb)
            elif (tb_add_options == 1 and d_lb > 1):
                x_value = random.randint(1, d_lb) * (-1)
        else:
            y_value = 0

            tb_add_options = random.randint(0, 2)
            if (tb_add_options == 0 and d_rb > 1):
                x_value = random.randint(1, d_rb)
            elif (tb_add_options == 1 and d_lb > 1):
                x_value = random.randint(1, d_lb) * (-1)
    ####===> to right <===####
    elif (trans_m_options == 2 and d_rb > 1):
        x_value = random.randint(1, d_rb)
        y_value = 0
    ####===> to left <====####
    elif (trans_m_options == 3 and d_lb > 1):
        x_value = random.randint(1, d_lb) * (-1)
        y_value = 0

    M_transformation = np.float32([[1, 0, x_value], [0, 1, y_value]])
    dst_transformation = cv2.warpAffine(image_array, M_transformation,
                                        (cols, rows))
    convertPixelsToWhite(dst_transformation)

    return dst_transformation


def getPerspectiveTransformationOfImage(image_array):
    print('===> PERSPECTIVE TRANSFORMATION <===')

    cols, rows = getShapeInfo(image_array)

    corners_of_original = getCornersOfDrawingFrame(
        getCalcOfMaxMinValuesOfPixelHolder(image_array))
    corners_of_dst = getCornersOfDrawingFrame(
        getCalcOfMaxMinValuesOfPixelHolder(image_array))

    new_distances = getDistances(
        getCalcOfMaxMinValuesOfPixelHolder(image_array), image_array)
    d_bb, d_rb, d_tb, d_lb = new_distances

    trans_m_options = random.randint(0, 2)

    ####===> stretch/compress top and bottom <===####
    if (trans_m_options == 0):
        print('====> stretch top and bottom <====')
        vertical_add_options = random.randint(0, 2)

        # stretch/compress ONE corner - top
        if (vertical_add_options == 0):
            print('=====> stretch/compress ONE corner - top <=====')
            corner_index = random.randint(0, 1)
            corners_of_dst[corner_index][1] = corners_of_dst[
                corner_index][1] + (random.randint(1, 5) if random.randint(
                    0, 1) == 0 else random.randint(1, 5) * -1)
        # stretch/compress ONE corner - bottom
        elif (vertical_add_options == 1):
            print('=====> stretch/compress ONE corner - bottom <=====')
            corner_index = random.randint(2, 3)
            corners_of_dst[corner_index][1] = corners_of_dst[
                corner_index][1] + (random.randint(1, 5) if random.randint(
                    0, 1) == 0 else random.randint(1, 5) * -1)
        # stretch/compress BOTH corners - top/bottom
        else:
            top_or_bottom = random.choice([[0, 1], [2, 3], [0, 1, 'equal'],
                                           [2, 3, 'equal']])
            # UNEQUAL top
            if (top_or_bottom == [0, 1]):
                print(
                    '=====> stretch/compress BOTH corners - UNEQUAL top <====='
                )

                corners_of_dst[top_or_bottom[0]][1] = corners_of_dst[
                    top_or_bottom[0]][1] + (random.randint(1, 5) if
                                            (random.randint(0, 1) == 0) else
                                            random.randint(1, 5) * -1)
                corners_of_dst[top_or_bottom[1]][1] = corners_of_dst[
                    top_or_bottom[1]][1] + (random.randint(1, 5) if
                                            (random.randint(0, 1) == 0) else
                                            random.randint(1, 5) * -1)
            # UNEQUAL bottom
            elif (top_or_bottom == [2, 3]):
                print(
                    '=====> stretch/compress BOTH corners - UNEQUAL bottom <====='
                )

                corners_of_dst[top_or_bottom[0]][1] = corners_of_dst[
                    top_or_bottom[0]][1] + (random.randint(1, 5) if
                                            (random.randint(0, 1) == 0) else
                                            random.randint(1, 5) * -1)
                corners_of_dst[top_or_bottom[1]][1] = corners_of_dst[
                    top_or_bottom[1]][1] + (random.randint(1, 5) if
                                            (random.randint(0, 1) == 0) else
                                            random.randint(1, 5) * -1)
            # EQUAL top
            elif (top_or_bottom == [0, 1, 'equal']):
                print(
                    '=====> stretch/compress BOTH corners - EQUAL top <=====')

                equal_stretch_compress = random.randint(1, 5) if (
                    random.randint(0, 1) == 0) else random.randint(1, 5) * -1
                corners_of_dst[top_or_bottom[0]][1] = corners_of_dst[
                    top_or_bottom[0]][1] + equal_stretch_compress
                corners_of_dst[top_or_bottom[1]][1] = corners_of_dst[
                    top_or_bottom[1]][1] + equal_stretch_compress
            # EQUAL bottom
            else:
                print(
                    '=====> stretch/compress BOTH corners - EQUAL bottom <====='
                )

                equal_stretch_compress = random.randint(1, 5) if (
                    random.randint(0, 1) == 0) else random.randint(1, 5) * -1
                corners_of_dst[top_or_bottom[0]][1] = corners_of_dst[
                    top_or_bottom[0]][1] + equal_stretch_compress
                corners_of_dst[top_or_bottom[1]][1] = corners_of_dst[
                    top_or_bottom[1]][1] + equal_stretch_compress

    ####===> stretch to right and left <===####
    elif (trans_m_options == 1):
        print('====> stretch to right and left <====')

        horizontal_add_options = random.randint(0, 2)

        # stretch/compress ONE corner - left
        if (horizontal_add_options == 0):
            print('=====> stretch/compress ONE corner - left <=====')
            corner_index = 0 if random.randint(0, 1) == 0 else 2
            corners_of_dst[corner_index][
                0] = corners_of_dst[corner_index][0] + (
                    random.randint(1, 5) if
                    (random.randint(0, 1) == 0) else random.randint(1, 5) * -1)
        # stretch/compress ONE corner - right
        elif (horizontal_add_options == 1):
            print('=====> stretch/compress ONE corner - right <=====')
            corner_index = 1 if random.randint(0, 1) == 0 else 3
            corners_of_dst[corner_index][
                0] = corners_of_dst[corner_index][0] + (
                    random.randint(1, 5) if
                    (random.randint(0, 1) == 0) else random.randint(1, 5) * -1)
        # stretch/compress BOTH corners - left/right
        else:
            left_or_right = random.choice([[0, 2], [1, 3], [0, 2, 'equal'],
                                           [1, 3, 'equal']])
            # UNEQUAL left
            if (left_or_right == [0, 2]):
                print(
                    '=====> stretch/compress BOTH corners - UNEQUAL top <====='
                )

                corners_of_dst[left_or_right[0]][0] = corners_of_dst[
                    left_or_right[0]][0] + (random.randint(1, 5)
                                            if random.randint(0, 1) == 0 else
                                            random.randint(1, 5) * -1)
                corners_of_dst[left_or_right[1]][0] = corners_of_dst[
                    left_or_right[1]][0] + (random.randint(1, 5)
                                            if random.randint(0, 1) == 0 else
                                            random.randint(1, 5) * -1)
            # UNEQUAL right
            elif (left_or_right == [1, 3]):
                print(
                    '=====> stretch/compress BOTH corners - UNEQUAL bottom <====='
                )

                corners_of_dst[left_or_right[0]][0] = corners_of_dst[
                    left_or_right[0]][0] + (random.randint(1, 5)
                                            if random.randint(0, 1) == 0 else
                                            random.randint(1, 5) * -1)
                corners_of_dst[left_or_right[1]][0] = corners_of_dst[
                    left_or_right[1]][0] + (random.randint(1, 5)
                                            if random.randint(0, 1) == 0 else
                                            random.randint(1, 5) * -1)
            # EQUAL left
            elif (left_or_right == [0, 2, 'equal']):
                print(
                    '=====> stretch/compress BOTH corners - EQUAL top <=====')

                equal_stretch_compress = random.randint(1, 5) if (
                    random.randint(0, 1) == 0) else random.randint(1, 5) * -1
                corners_of_dst[left_or_right[0]][0] = corners_of_dst[
                    left_or_right[0]][0] + equal_stretch_compress
                corners_of_dst[left_or_right[1]][0] = corners_of_dst[
                    left_or_right[1]][0] + equal_stretch_compress
            # EQUAL RIGHT
            else:
                print(
                    '=====> stretch/compress BOTH corners - EQUAL bottom <====='
                )

                equal_stretch_compress = random.randint(1, 5) if (
                    random.randint(0, 1) == 0) else random.randint(1, 5) * -1
                corners_of_dst[left_or_right[0]][0] = corners_of_dst[
                    left_or_right[0]][0] + equal_stretch_compress
                corners_of_dst[left_or_right[1]][0] = corners_of_dst[
                    left_or_right[1]][0] + equal_stretch_compress

    ####===> multiple stretch/compress options in one <===####
    else:
        print('====> multiple stretch/compress options in one <====')
        corners_of_dst[0][0] = corners_of_dst[0][0] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[0][1] = corners_of_dst[0][1] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[1][0] = corners_of_dst[1][0] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[1][1] = corners_of_dst[1][1] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[2][0] = corners_of_dst[2][0] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[2][1] = corners_of_dst[2][1] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[3][0] = corners_of_dst[3][0] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)
        corners_of_dst[3][1] = corners_of_dst[3][1] + (
            round(random.uniform(1, 2), 2) if
            (random.randint(0, 1) == 0) else round(random.uniform(1, 2), 2) *
            -1)

    start_points = np.float32(corners_of_original)
    dst_points = np.float32(corners_of_dst)

    M_transformation = cv2.getPerspectiveTransform(start_points, dst_points)
    dst_transformation = cv2.warpPerspective(image_array, M_transformation,
                                             (cols, rows))
    convertPixelsToWhite(dst_transformation)

    return dst_transformation


def getRotationOfImage(image_array):
    print('===> ROTATION <===')

    cols, rows = getShapeInfo(image_array)

    scale = 1
    list_corners = getCornersOfDrawingFrame(
        getCalcOfMaxMinValuesOfPixelHolder(image_array))
    copy_corners = copy.copy(list_corners)
    copy_corners = [[math.floor(value * scale) for value in corner]
                    for corner in copy_corners]

    x_center = list_corners[0][0] + math.floor(
        (list_corners[1][0] - list_corners[0][0]) / 2)
    y_center = list_corners[0][1] + math.floor(
        (list_corners[2][1] - list_corners[0][1]) / 2)

    d_tb = copy_corners[0][1]
    d_rb = cols - copy_corners[1][0]
    d_lb = copy_corners[0][0]
    d_bb = rows - copy_corners[2][1]

    angle_0 = math.degrees(
        math.atan(math.tan(d_tb / (copy_corners[1][0] - copy_corners[0][0]))))
    angle_1 = math.degrees(
        math.atan(math.tan(d_rb / (copy_corners[3][1] - copy_corners[1][1]))))
    angle_2 = math.degrees(
        math.atan(math.tan(d_lb / (copy_corners[2][1] - copy_corners[0][1]))))
    angle_3 = math.degrees(
        math.atan(math.tan(d_bb / (copy_corners[3][0] - copy_corners[2][0]))))

    max_rot_angle = round(min([angle_0, angle_1, angle_2, angle_3]), 2)
    rot = random.uniform(-max_rot_angle, max_rot_angle)

    M_transformation = cv2.getRotationMatrix2D((x_center, y_center), rot,
                                               scale)
    dst_transformation = cv2.warpAffine(image_array, M_transformation,
                                        (cols, rows))
    convertPixelsToWhite(dst_transformation)

    return dst_transformation


def getScaleOfImage(image_array):
    print('===> SCALE <===')

    cols, rows = getShapeInfo(image_array)

    scale = round(random.uniform(0.65, 0.95), 2)
    list_corners = getCornersOfDrawingFrame(
        getCalcOfMaxMinValuesOfPixelHolder(image_array))

    div_x = round(random.uniform(1.75, 2.25), 3)
    div_y = round(random.uniform(1.75, 2.25), 3)

    x_center = list_corners[0][0] + math.floor(
        (list_corners[1][0] - list_corners[0][0]) / div_x)
    y_center = list_corners[0][1] + math.floor(
        (list_corners[2][1] - list_corners[0][1]) / div_y)

    M_transformation = cv2.getRotationMatrix2D((x_center, y_center), 0, scale)
    dst_transformation = cv2.warpAffine(image_array, M_transformation,
                                        (cols, rows))
    convertPixelsToWhite(dst_transformation)

    return dst_transformation


def createSamples(image_array, shape):
    transformation_options = random.randint(0, 13)

    ###############
    # translation #
    ###############
    if (transformation_options == 0):
        result_image_array = getTranslationOfImage(image_array)

    ############
    # rotation #
    ############
    elif (transformation_options == 1):
        result_image_array = getRotationOfImage(image_array)

    ###########
    # scaling #
    ###########
    elif (transformation_options == 2):
        result_image_array = getScaleOfImage(image_array)

    ##############################
    # perspective transformation #
    ##############################
    elif (transformation_options == 3):
        result_image_array = getPerspectiveTransformationOfImage(image_array)

    ##########################
    # translation + rotation #
    ##########################
    elif (transformation_options == 4):
        trans_rot_options = random.randint(0, 1)

        # 1st trans, 2nd rot
        if (trans_rot_options == 0):
            trans_dst = getTranslationOfImage(image_array)
            result_image_array = getRotationOfImage(trans_dst)
        # 1st rot, 2nd trans
        else:
            rot_dst = getRotationOfImage(image_array)
            result_image_array = getTranslationOfImage(rot_dst)
    ##########################
    # translation + scaling #
    ##########################
    elif (transformation_options == 5):
        trans_scale_options = random.randint(0, 1)

        # 1st trans, 2nd scale
        if (trans_scale_options == 0):
            trans_dst = getTranslationOfImage(image_array)
            result_image_array = getScaleOfImage(trans_dst)
        # 1st scale, 2nd trans
        else:
            scale_dst = getScaleOfImage(image_array)
            result_image_array = getTranslationOfImage(scale_dst)
    ############################################
    # translation + perspective transformation #
    ############################################
    elif (transformation_options == 6):
        transl_pTransf_options = random.randint(0, 1)

        # 1st transl, 2nd pTransf
        if (transl_pTransf_options == 0):
            transl_dst = getTranslationOfImage(image_array)
            result_image_array = getPerspectiveTransformationOfImage(
                transl_dst)
        # 1st pTransf, 2nd transl
        else:
            pTransf_dst = getPerspectiveTransformationOfImage(image_array)
            result_image_array = getTranslationOfImage(pTransf_dst)
    #########################################
    # rotation + perspective transformation #
    #########################################
    elif (transformation_options == 7):
        rot_pTransf_options = random.randint(0, 1)

        # 1st rot, 2nd pTransf
        if (rot_pTransf_options == 0):
            rot_dst = getRotationOfImage(image_array)
            result_image_array = getPerspectiveTransformationOfImage(rot_dst)
        # 1st pTransf, 2nd rot
        else:
            pTransf_dst = getPerspectiveTransformationOfImage(image_array)
            result_image_array = getRotationOfImage(pTransf_dst)
    #########################################
    # rotation + scaling #
    #########################################
    elif (transformation_options == 8):
        rot_scale_options = random.randint(0, 1)

        # 1st rot, 2nd scale
        if (rot_scale_options == 0):
            rot_dst = getRotationOfImage(image_array)
            result_image_array = getScaleOfImage(rot_dst)
        # 1st scale, 2nd rot
        else:
            scale_dst = getScaleOfImage(image_array)
            result_image_array = getRotationOfImage(scale_dst)
    #########################################
    # scaling + perspective transformation #
    #########################################
    elif (transformation_options == 9):
        scale_pTransf_options = random.randint(0, 1)

        # 1st scale, 2nd pTransf
        if (scale_pTransf_options == 0):
            scale_dst = getScaleOfImage(image_array)
            result_image_array = getPerspectiveTransformationOfImage(scale_dst)
        # 1st pTransf, 2nd scale
        else:
            pTransf_dst = getPerspectiveTransformationOfImage(image_array)
            result_image_array = getScaleOfImage(pTransf_dst)
    #######################################################
    # translation + rotation + perspective transformation #
    #######################################################
    elif (transformation_options == 10):
        transl_rot_pTransf_options = random.randint(0, 5)

        # 1st transl, 2nd rot, 3rd pTransf
        if (transl_rot_pTransf_options == 0):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_rot_dst = getRotationOfImage(transl_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    transl_rot_dst)
            except Exception as e:
                print(e)
                pass
        # 1st transl, 2nd pTransf, 3rd rot
        elif (transl_rot_pTransf_options == 1):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_pTransf_dst = getPerspectiveTransformationOfImage(
                    transl_dst)
                result_image_array = getRotationOfImage(transl_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd transl, 3rd pTransf
        elif (transl_rot_pTransf_options == 2):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_transl_dst = getTranslationOfImage(rot_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    rot_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd pTransf, 3rd transl
        elif (transl_rot_pTransf_options == 3):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_pTransf_dst = getPerspectiveTransformationOfImage(rot_dst)
                result_image_array = getTranslationOfImage(rot_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd transl, 3rd rot
        elif (transl_rot_pTransf_options == 4):
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_transl_dst = getTranslationOfImage(pTransf_dst)
                result_image_array = getRotationOfImage(pTransf_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd rot, 3rd transl
        else:
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_rot_dst = getRotationOfImage(pTransf_dst)
                result_image_array = getTranslationOfImage(pTransf_rot_dst)
            except Exception as e:
                print(e)
                pass
    ######################################################
    # translation + scaling + perspective transformation #
    ######################################################
    elif (transformation_options == 11):
        transl_scale_pTransf_options = random.randint(0, 5)

        # 1st transl, 2nd scale, 3rd pTransf
        if (transl_scale_pTransf_options == 0):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_scale_dst = getScaleOfImage(transl_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    transl_scale_dst)
            except Exception as e:
                print(e)
                pass
        # 1st transl, 2nd pTransf, 3rd scale
        elif (transl_scale_pTransf_options == 1):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_pTransf_dst = getPerspectiveTransformationOfImage(
                    transl_dst)
                result_image_array = getScaleOfImage(transl_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st scale, 2nd transl, 3rd pTransf
        elif (transl_scale_pTransf_options == 2):
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_transl_dst = getTranslationOfImage(scale_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    scale_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st scale, 2nd pTransf, 3rd transl
        elif (transl_scale_pTransf_options == 3):
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_pTransf_dst = getPerspectiveTransformationOfImage(
                    scale_dst)
                result_image_array = getTranslationOfImage(scale_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd transl, 3rd scale
        elif (transl_scale_pTransf_options == 4):
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_transl_dst = getTranslationOfImage(pTransf_dst)
                result_image_array = getScaleOfImage(pTransf_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd scale, 3rd transl
        else:
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_scale_dst = getScaleOfImage(pTransf_dst)
                result_image_array = getTranslationOfImage(pTransf_scale_dst)
            except Exception as e:
                print(e)
                pass
    ###################################################
    # scaling + rotation + perspective transformation #
    ###################################################
    elif (transformation_options == 12):
        scale_rot_pTransf_options = random.randint(0, 5)

        # 1st scale, 2nd rot, 3rd pTransf
        if (scale_rot_pTransf_options == 0):
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_rot_dst = getRotationOfImage(scale_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    scale_rot_dst)
            except Exception as e:
                print(e)
                pass
        # 1st scale, 2nd pTransf, 3rd rot
        elif (scale_rot_pTransf_options == 1):
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_pTransf_dst = getPerspectiveTransformationOfImage(
                    scale_dst)
                result_image_array = getRotationOfImage(scale_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd scale, 3rd pTransf
        elif (scale_rot_pTransf_options == 2):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_scale_dst = getScaleOfImage(rot_dst)
                result_image_array = getPerspectiveTransformationOfImage(
                    rot_scale_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd pTransf, 3rd scale
        elif (scale_rot_pTransf_options == 3):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_pTransf_dst = getPerspectiveTransformationOfImage(rot_dst)
                result_image_array = getScaleOfImage(rot_pTransf_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd scale, 3rd rot
        elif (scale_rot_pTransf_options == 4):
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_scale_dst = getScaleOfImage(pTransf_dst)
                result_image_array = getRotationOfImage(pTransf_scale_dst)
            except Exception as e:
                print(e)
                pass
        # 1st pTransf, 2nd rot, 3rd scale
        else:
            try:
                pTransf_dst = getPerspectiveTransformationOfImage(image_array)
                pTransf_rot_dst = getRotationOfImage(pTransf_dst)
                result_image_array = getScaleOfImage(pTransf_rot_dst)
            except Exception as e:
                print(e)
                pass
    ####################################
    # translation + rotation + scaling #
    ####################################
    elif (transformation_options == 13):
        transl_rot_scale_options = random.randint(0, 5)

        # 1st transl, 2nd rot, 3rd scale
        if (transl_rot_scale_options == 0):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_rot_dst = getRotationOfImage(transl_dst)
                result_image_array = getScaleOfImage(transl_rot_dst)
            except Exception as e:
                print(e)
                pass
        # 1st transl, 2nd scale, 3rd rot
        elif (transl_rot_scale_options == 1):
            try:
                transl_dst = getTranslationOfImage(image_array)
                transl_scale_dst = getScaleOfImage(transl_dst)
                result_image_array = getRotationOfImage(transl_scale_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd transl, 3rd scale
        elif (transl_rot_scale_options == 2):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_transl_dst = getTranslationOfImage(rot_dst)
                result_image_array = getScaleOfImage(rot_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st rot, 2nd scale, 3rd transl
        elif (transl_rot_scale_options == 3):
            try:
                rot_dst = getRotationOfImage(image_array)
                rot_scale_dst = getScaleOfImage(rot_dst)
                result_image_array = getTranslationOfImage(rot_scale_dst)
            except Exception as e:
                print(e)
                pass
        # 1st scale, 2nd transl, 3rd rot
        elif (transl_rot_scale_options == 4):
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_transl_dst = getTranslationOfImage(scale_dst)
                result_image_array = getRotationOfImage(scale_transl_dst)
            except Exception as e:
                print(e)
                pass
        # 1st scale, 2nd rot, 3rd transl
        else:
            try:
                scale_dst = getScaleOfImage(image_array)
                scale_rot_dst = getRotationOfImage(scale_dst)
                result_image_array = getTranslationOfImage(scale_rot_dst)
            except Exception as e:
                print(e)
                pass
    #################################################################
    # translation + rotation + perspective transformation + scaling #
    #################################################################
    # elif (transformation_options == 14):
    #     ---- Hier müssten 24 Optionen entstehen, damit man alle Faelle
    #     ---- abdeckt, weswegen dies erst einmal ausgelassen wird.
    #     scale_rot_pTransf_options = random.randint(0, 23)

    try:
        samples_list.append(result_image_array)
        shape_list.append(shape)
        print('||=====> SAMPLE HAS BEEN CREATED <=====||')
    except Exception as e:
        print(e)
        pass


# returns the list of samples
def getSamplesList():
    return samples_list


# returns a list with lists of converted ndarrays to use them in a json-message
def getSamplesListForJSON():
    global samples_list

    json_list = []

    for sample in samples_list:
        json_list.append(sample.tolist())

    return json_list


# returns the list of shapes
def getShapeList():
    return shape_list


# clear both lists
def clearBothDataLists():
    global samples_list
    global shape_list

    samples_list.clear()
    shape_list.clear()