from framework import Framework, main
from xml_box2d import world_from_xml, find_joint, find_body
import numpy as np
from operator import add


class Hopper(Framework):

    name = "Hopper"

    def __init__(self):
        with open("hopper.xml", "r") as f:
            s = f.read()
        world = world_from_xml(s)
        super(Hopper, self).__init__(world)
        joints = [
            find_joint(world, "thigh_joint"),
            find_joint(world, "leg_joint"),
            find_joint(world, "foot_joint"),
        ]
        bodies = [
            find_body(world, "torso"),
            find_body(world, "thigh"),
            find_body(world, "leg"),
            find_body(world, "foot"),
        ]
        self.joints = joints
        self.bodies = bodies
        self.cnt = 0
        # for body in bodies:
        #     body.

    def Step(self, settings):
        ctrls = np.random.randn(len(self.bodies))
        # for idx, body in enumerate(self.bodies):
        #     body.ApplyTorque(ctrls[idx], True)
        # if self.cnt % 10 == 0:
        # self.cnt += 1
        # #print ctrls
        for idx, joint in enumerate(self.joints):
            joint.motorEnabled = True
            joint.motorSpeed = ctrls[idx]*10
            joint.maxMotorTorque = 1000

        com_pos = reduce(add, [x.mass * x.worldCenter for x in self.bodies])
        com_vel = reduce(add, [x.mass * x.linearVelocity for x in self.bodies])

        pos = [x.worldCenter for x in self.bodies]
        rot = [x.angle for x in self.bodies]

        linvel = [x.linearVelocity for x in self.bodies]
        angvel = [x.angularVelocity for x in self.bodies]


        # xpos = [x.position for x in self.bodies]
        # qpos = [

        print com_pos, com_vel
    
        # for body in self.bodies:
        #     print body.userData["name"], body.linearVelocity

        super(Hopper, self).Step(settings)

if __name__ == "__main__":
    main(Hopper)
