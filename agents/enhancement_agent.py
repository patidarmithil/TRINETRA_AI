import cv2

class EnhancementAgent:

    def enhance(self,image):

        img = cv2.imread(image)

        img = cv2.convertScaleAbs(
            img,
            alpha=1.3,
            beta=20
        )

        return img