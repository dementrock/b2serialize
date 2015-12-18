from parser.xml_box2d import world_from_xml, find_body
import numpy as np
from box2d_viewer import Box2DViewer


class Box2DMDP(object):

    def __init__(self, xml_path):
        with open(xml_path, "r") as f:
            s = f.read()
        world, extra_data = world_from_xml(s)
        self.world = world
        self.extra_data = extra_data
        self.initial_state = self.get_state()
        self.current_state = self.initial_state
        self.viewer = None

    def set_state(self, state):
        splitted = np.array(state).reshape((-1, 6))
        for body, body_state in zip(self.world.bodies, splitted):
            xpos, ypos, apos, xvel, yvel, avel = body_state
            body.position = (xpos, ypos)
            body.angle = apos
            body.linearVelocity = (xvel, yvel)
            body.angularVelocity = avel

    def reset(self):
        self.set_state(self.initial_state)
        return self.get_state(), self.get_obs()

    def get_state(self):
        s = []
        for body in self.world.bodies:
            s.append(np.concatenate([
                list(body.position),
                [body.angle],
                list(body.linearVelocity),
                [body.angularVelocity]
            ]))
        return np.concatenate(s)

    @property
    def action_dim(self):
        return len(self.extra_data.controls)

    def step(self, state, action):
        if len(action) != self.action_dim:
            raise ValueError('incorrect action dimension: expected %d but got '
                             '%d' % (self.action_dim, len(action)))
        if not np.array_equal(state, self.current_state):
            self.set_state(state)
        for ctrl, act in zip(self.extra_data.controls, action):
            if ctrl.typ == "force":
                body = find_body(self.world, ctrl.body)
                direction = np.array(ctrl.direction)
                direction = direction / np.linalg.norm(direction)
                world_force = body.GetWorldVector(direction * act)
                world_point = body.GetWorldPoint(ctrl.anchor)
                body.ApplyForce(world_force, world_point, wake=True)
            else:
                raise NotImplementedError
        self.world.Step(
            self.extra_data.timeStep,
            self.extra_data.velocityIterations,
            self.extra_data.positionIterations
        )
        return self.get_state(), self.get_obs()

    def get_obs(self):
        obs = []
        for state in self.extra_data.states:
            body = find_body(self.world, state.body)
            if state.typ == "xpos":
                obs.append(body.position[0])
            elif state.typ == "ypos":
                obs.append(body.position[1])
            elif state.typ == "xvel":
                obs.append(body.linearVelocity[0])
            elif state.typ == "yvel":
                obs.append(body.linearVelocity[1])
            elif state.typ == "apos":
                obs.append(body.angle)
            elif state.typ == "avel":
                obs.append(body.angularVelocity)
            else:
                raise NotImplementedError
        return np.array(obs)

    def start_viewer(self):
        if not self.viewer:
            self.viewer = Box2DViewer(self.world)

    def stop_viewer(self):
        if self.viewer:
            self.viewer.finish()
        self.viewer = None

    def plot(self):
        if self.viewer:
            self.viewer.loop_once()
