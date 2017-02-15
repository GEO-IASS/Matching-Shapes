import cozmo
import asyncio
from Common.woc import WOC
from Common.colors import Colors
import sys
from math import degrees, atan2, sqrt, asin
import http.client
import ast
import json
from random import randint

try:
    import numpy as np
except ImportError:
    sys.exit("Cannot import numpy: Do `pip3 install --user numpy` to install")

try:
    from PIL import Image
    from PIL import ImageFilter
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

'''
@class ShapeBuilder
Use the blocks to create the shape that's shown on Cozmo's face.
@author - Wizards of Coz
'''

class ShapeBuilder():
    IMAGES_FOLDER = "Images"
    CUBE_SIZE = 45
    ERROR_MARGIN = 5
    ANGLE_MARGIN = 15
    TOTAL_IMAGES = 8
    HAPPY_ANIMS = ["anim_freeplay_reacttoface_sayname_01","anim_memorymatch_successhand_cozmo_02","anim_rtpmemorymatch_yes_01","anim_rtpmemorymatch_yes_04"]
    SAD_ANIMS = ["anim_bored_getout_02","anim_reacttoblock_frustrated_01","anim_bored_event_02"]
    WIN_ANIM = "anim_memorymatch_successhand_cozmo_04"
    BORED_ANIM = []
    SERVER_IP = "128.237.202.46:5000"

    playerNumber = -1;
    foundWinner = False

    def __init__(self, *a, **kw):

        cozmo.setup_basic_logging()
        try:
            cozmo.connect_with_tkviewer(self.run, force_on_top=True)
        except cozmo.ConnectionError as e:
            sys.exit("A connection error occurred: %s" % e)
        # cozmo.connect(self.run)

    async def pollWinner(self):

        while self.foundWinner is False:
            self.conn.request("GET", "/getWinner")
            response = self.conn.getresponse()
            data = response.read()
            decodedData = data.decode('UTF-8')
            datadict = ast.literal_eval(decodedData);
            serverWinner = int(datadict['winner']);
            if serverWinner != 0:
                self.foundWinner = True;
                if serverWinner == self.playerNumber:
                    print("You win")
                else:
                    print("LOSE");
                    self.exit_flag = True
                    self.coz.abort_all_actions();
                    await asyncio.sleep(0.2);
                    await self.coz.play_anim("anim_memorymatch_failgame_cozmo_02").wait_for_completed()
            await asyncio.sleep(1)
            self.conn.close()

    async def run(self, coz_conn):
        asyncio.set_event_loop(coz_conn._loop)
        self.coz = await coz_conn.wait_for_robot()

        self.exit_flag = False

        conn_success = await self.connectToServer();
        if conn_success:
            asyncio.ensure_future(self.pollWinner());

        asyncio.ensure_future(self.start_program());

        # while not self.exit_flag:
        while True:
            await asyncio.sleep(0)
        self.coz.abort_all_actions()

    async def PostWinToServer(self):

        dict = {'playernum': str(self.playerNumber)}
        params = json.dumps(dict);
        headers = {"Content-type": "application/json"}
        self.conn.request("POST", "/iAmDone", params, headers)
        response = self.conn.getresponse()
        self.conn.close();

    async def PostSuccessToServer(self):

        dict = {'playernum': str(self.playerNumber),'number':str(self.currentImage)}
        params = json.dumps(dict);
        headers = {"Content-type": "application/json"}
        self.conn.request("POST", "/success", params, headers)
        response = self.conn.getresponse()
        self.conn.close();

    async def connectToServer(self):
        currentPlayerName = "Cozmo";
        try:
            self.conn = http.client.HTTPConnection(self.SERVER_IP);
            dict = {'playername': str(currentPlayerName)}
            params = json.dumps(dict);
            headers = {"Content-type": "application/json"}
            self.conn.request("POST", "/connectToGame", params, headers)
            response = self.conn.getresponse()
            data = response.read()
            decodedData = data.decode('UTF-8')
            datadict = ast.literal_eval(decodedData);
            self.playerNumber = int(datadict['playerNum']);
            self.conn.close();
            return True
        except:
            print("Server not on");
            return False

    async def start_program(self):
        self.found_match = False;
        print(cozmo.oled_face.dimensions());
        self.coz.camera.image_stream_enabled = True;
        await self.coz.set_lift_height(0).wait_for_completed();
        await self.coz.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 4).wait_for_completed()
        self.cubes = None
        look_around = self.coz.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

        try:
            self.cubes = await self.coz.world.wait_until_observe_num_objects(3, object_type = cozmo.objects.LightCube,timeout=60)
        except asyncio.TimeoutError:
            print("Didn't find a cube :-(")
            return
        finally:
            look_around.stop()
            for i in range(0,3):
                for cube in self.cubes:
                    cube.set_lights(Colors.GREEN);
                await asyncio.sleep(0.3);
                for cube in self.cubes:
                    cube.set_lights_off();
                await asyncio.sleep(0.3);

            self.positions = []
            self.rotations = []
            for i in range(0, len(self.cubes)):
                self.positions.append(self.cubes[i].pose.position);
                self.rotations.append(self.cubes[i].pose.rotation);

            self.currentImage = 7
            await self.showNextShape()

    async def showNextShape(self):
        self.currentImage += 1;

        if self.exit_flag == True or self.currentImage > self.TOTAL_IMAGES:
            self.exit_flag = True
            return;

        self.found_match = False

        await self.coz.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE / 4).wait_for_completed()

        asyncio.ensure_future(self.display_shape());

        self.still_count = 0;
        was_success = True
        while not self.found_match:
            did_change = False
            for i in range(0, len(self.cubes)):
                pos1 = self.positions[i]
                pos2 = self.cubes[i].pose.position
                rot1 = self.cubes[i].pose.rotation.angle_z.degrees;
                rot2 = self.rotations[i].angle_z.degrees;
                dist = sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)
                distRotation = abs(rot1-rot2);
                if dist < 1 and distRotation < 5:
                    continue;
                did_change = True
                self.positions[i] = self.cubes[i].pose.position;
                self.rotations[i] = self.cubes[i].pose.rotation;

            if did_change == True:
                self.still_count = 0;
                self.found_match = await self.checkPattern();
            else:
                self.still_count += 1;
                if (self.still_count > 5):
                    self.still_count = 0
                    for cube in self.cubes:
                        cube.set_lights(Colors.RED);
                    self.coz.set_all_backpack_lights(Colors.RED)

                    self.found_match = True

                    if self.exit_flag == False:
                        self.coz.abort_all_actions()
                        await self.coz.play_anim(self.SAD_ANIMS[randint(0, len(self.SAD_ANIMS) - 1)]).wait_for_completed()

                        for cube in self.cubes:
                            cube.set_lights_off();
                        self.coz.set_backpack_lights_off();

                    self.currentImage -= 1;
                    was_success = False
                    break
            await asyncio.sleep(0.8)

        if was_success:
            for cube in self.cubes:
                cube.set_lights(Colors.GREEN);
            self.coz.set_all_backpack_lights(Colors.GREEN)
            await self.animate_block_success()

            await asyncio.sleep(1);

            for cube in self.cubes:
                cube.set_lights_off();
            self.coz.set_backpack_lights_off();

        await self.showNextShape();

    async def checkPattern(self):
        # x-axis is depth, y-axis is left-right and z-axis is height
        if self.currentImage == 1:      # Tower
            z = []
            z.append(self.positions[0].z)
            z.append(self.positions[1].z)
            z.append(self.positions[2].z)

            z.sort();
            if(abs(z[1] - z[0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(z[1] - z[0]) < self.CUBE_SIZE + self.ERROR_MARGIN and abs(z[2] - z[1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(z[2] - z[1]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                return True

        elif self.currentImage == 2:    # Letter-L
            xz = [];
            xz.append((self.positions[0].z,self.positions[0].y))
            xz.append((self.positions[1].z, self.positions[1].y))
            xz.append((self.positions[2].z, self.positions[2].y))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) < self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                if((abs(xz[0][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN) or (abs(xz[1][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[2][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[2][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN)):
                    return True

        elif self.currentImage == 3:    # Triangle
            xz = [];
            xz.append((self.positions[0].z,self.positions[0].y))
            xz.append((self.positions[1].z, self.positions[1].y))
            xz.append((self.positions[2].z, self.positions[2].y))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > (self.CUBE_SIZE/2) - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < (self.CUBE_SIZE/2) + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > (self.CUBE_SIZE/2) - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < (self.CUBE_SIZE/2) + self.ERROR_MARGIN):
                if(abs(xz[0][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                    return True

        elif self.currentImage == 4:    # skewed tower
            xz = [];
            xz.append((self.positions[0].y,self.positions[0].z))
            xz.append((self.positions[1].y, self.positions[1].z))
            xz.append((self.positions[2].y, self.positions[2].z))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < self.CUBE_SIZE + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                if(abs(xz[0][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > (self.CUBE_SIZE/2) - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < (self.CUBE_SIZE/2) + self.ERROR_MARGIN):
                    return True

        elif self.currentImage == 5:    # angled middle block in tower
            xz = [];
            xz.append((self.rotations[0].angle_z.degrees, self.positions[0].z))
            xz.append((self.rotations[1].angle_z.degrees, self.positions[1].z))
            xz.append((self.rotations[2].angle_z.degrees, self.positions[2].z))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < self.CUBE_SIZE + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                if((abs(xz[0][0] - xz[2][0]) % 90 < self.ANGLE_MARGIN or abs(xz[0][0] - xz[2][0]) % 90 > 90-self.ANGLE_MARGIN) and (abs(xz[0][0] - xz[1][0]) % 90 < 45+self.ANGLE_MARGIN and abs(xz[0][0] - xz[1][0]) % 90 > 45-self.ANGLE_MARGIN)):
                    return True

        elif self.currentImage == 6:    # Triangle
            xz = [];
            xz.append((self.positions[0].z,self.positions[0].y))
            xz.append((self.positions[1].z, self.positions[1].y))
            xz.append((self.positions[2].z, self.positions[2].y))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > (self.CUBE_SIZE * 0.8) - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < (self.CUBE_SIZE * 0.8) + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > (self.CUBE_SIZE * 0.8) - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < (self.CUBE_SIZE*0.8) + self.ERROR_MARGIN):
                if(abs(xz[0][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                    return True

        elif self.currentImage == 7:    # Staircase
            xz = [];
            xz.append((self.positions[0].z, self.positions[0].y))
            xz.append((self.positions[1].z, self.positions[1].y))
            xz.append((self.positions[2].z, self.positions[2].y))

            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > (self.CUBE_SIZE * 0.5) - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < (self.CUBE_SIZE * 0.5) + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > (self.CUBE_SIZE * 0.5) - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < (self.CUBE_SIZE*0.5) + self.ERROR_MARGIN):
                if(abs(xz[1][0] - xz[2][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[2][0]) < self.CUBE_SIZE + self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                    return True

        elif self.currentImage == 8:    # Triangle with center at an angle
            xz = [];
            xz.append((self.positions[0].z, self.positions[0].y, self.rotations[0].angle_z.degrees))
            xz.append((self.positions[1].z, self.positions[1].y, self.rotations[1].angle_z.degrees))
            xz.append((self.positions[2].z, self.positions[2].y, self.rotations[2].angle_z.degrees))
            xz.sort(key=lambda x: x[1])
            if (abs(xz[1][1] - xz[0][1]) > (self.CUBE_SIZE * 1) - self.ERROR_MARGIN and abs(xz[1][1] - xz[0][1]) < (self.CUBE_SIZE*1) + self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) > (self.CUBE_SIZE*1) - self.ERROR_MARGIN and abs(xz[2][1] - xz[1][1]) < (self.CUBE_SIZE*1) + self.ERROR_MARGIN):
                if(abs(xz[0][0] - xz[2][0]) < self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) > self.CUBE_SIZE - self.ERROR_MARGIN and abs(xz[1][0] - xz[0][0]) < self.CUBE_SIZE + self.ERROR_MARGIN):
                    if ((abs(xz[0][2] - xz[2][2]) % 90 < self.ANGLE_MARGIN or abs(xz[0][2] - xz[2][2]) % 90 > 90 - self.ANGLE_MARGIN) and (abs(xz[0][2] - xz[1][2]) % 90 < 45 + self.ANGLE_MARGIN and abs(xz[0][2] - xz[1][2]) % 90 > 45 - self.ANGLE_MARGIN)):
                        return True

        elif self.currentImage == 9:    # angled block
            xz = [];
            xz.append((self.rotations[0].angle_z.degrees, self.positions[0].y, self.rotations[0]))
            xz.append((self.rotations[1].angle_z.degrees, self.positions[1].y, self.rotations[1]))
            xz.append((self.rotations[2].angle_z.degrees, self.positions[2].y, self.rotations[2]))

            xz.sort(key=lambda x: x[1])
            if (xz[1][1] - xz[0][1] > (self.CUBE_SIZE * 1.1) - self.ERROR_MARGIN and xz[1][1] - xz[0][1] < (self.CUBE_SIZE * 1.1) + self.ERROR_MARGIN and xz[2][1] - xz[1][1] > (self.CUBE_SIZE * 1.1) - self.ERROR_MARGIN and xz[2][1] - xz[1][1] < (self.CUBE_SIZE * 1.1) + self.ERROR_MARGIN):
                if ((abs(xz[0][0] - xz[2][0]) % 90 < self.ANGLE_MARGIN or abs(xz[0][0] - xz[2][0]) % 90 > 90 - self.ANGLE_MARGIN) and (abs(xz[0][0] - xz[1][0]) % 90 < self.ANGLE_MARGIN or abs(xz[0][0] - xz[1][0]) % 90 > 90 - self.ANGLE_MARGIN)):
                    eulers = await self._quat2equatorial(xz[1][2].q0_q1_q2_q3)
                    print(str(xz[1][2].q0_q1_q2_q3) + " - " + str(eulers));

        return False


    async def _quat2equatorial(self,q):
        x = q[1]
        y = q[2]
        z = q[3]
        w = q[0]

        y = y*w - z*x
        y2 = 2*y
        _y = degrees(asin(y2));

        xa = 2*(w*x + y*z)
        xb = 1 - 2*(x*x + y*y)
        _x = degrees(atan2(xa,xb))

        za = 2*(z*w + x*y)
        zb = 1-2*(y*y + z*z)
        _z = degrees(atan2(za,zb))

        return [_x,_y,_z]


    async def display_shape(self):
        while not self.found_match and not self.exit_flag:
            image = Image.open(self.IMAGES_FOLDER + "/" + str(self.currentImage) + ".jpg")
            resized_image = image.resize(cozmo.oled_face.dimensions(), Image.BICUBIC)
            face_image = cozmo.oled_face.convert_image_to_screen_data(resized_image, invert_image=True)
            self.coz.display_oled_face_image(face_image, 0.1 * 1000.0)
            await asyncio.sleep(0.1);

    async def animate_block_success(self):
        maxX = 320
        maxY = 240
        maxX_2 = 160
        image = Image.open(self.IMAGES_FOLDER + "/" + str(self.currentImage) + ".jpg")
        img = image.convert('L')
        pix = img.load()
        for i in range(maxX_2-5, maxX_2+5):
            for j in range(0, maxY):
                pix[i, j] = 255;

        for k in range(0, 100):
            for i in range(0, maxX_2-5):
                for j in range(0, maxY):
                    pix[i, j] = pix[i + 5, j]
            for i in range(maxX - 1, maxX_2+5, -1):
                for j in range(0, maxY):
                    pix[i, j] = pix[i - 5, j]
            resized_image = img.resize(cozmo.oled_face.dimensions(), Image.BICUBIC)
            face_image = cozmo.oled_face.convert_image_to_screen_data(resized_image, invert_image=True)
            self.coz.display_oled_face_image(face_image, 0.1 * 1000.0)

        await self.PostSuccessToServer();

        await asyncio.sleep(1);
        if(self.currentImage == self.TOTAL_IMAGES):
            await self.coz.play_anim(self.WIN_ANIM).wait_for_completed()
            await self.PostWinToServer();
        else:
            await self.coz.play_anim(self.HAPPY_ANIMS[randint(0, len(self.HAPPY_ANIMS) - 1)]).wait_for_completed()

if __name__ == '__main__':
    ShapeBuilder()
