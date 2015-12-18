common = { friction: 0.9, density: 1, group: -1 }

box2d {
  world(gravity: [0, -9.8]) {
    body(name: :torso, type: :dynamic, position: [0, 1.25]) {
      capsule(common.merge(from: [0, 0.2], to: [0, -0.2], radius: 0.05))
    }
    body(name: :thigh, type: :dynamic, position: [0, 0.825]) {
      capsule(common.merge(from: [0, 0.205], to: [0, -0.205], radius: 0.05))
    }
    body(name: :leg, type: :dynamic, position: [0, 0.35]) {
      capsule(common.merge(from: [0, 0.25], to: [0, -0.25], radius: 0.04))
    }
    body(name: :foot, type: :dynamic, position: [0.065, 0.1]) {
      capsule(common.merge(from: [-0.195, 0], to: [0.195, 0], radius: 0.06, friction: 2.0))
    }
    body(name: :ground, type: :static, position: [0, 0]) {
      fixture(shape: :polygon, box: [100, 0.05], friction: 2.0, density: 1, group: -2)
    }
    joint(
      type: :revolute,
      name: :thigh_joint,
      bodyA: :torso,
      bodyB: :thigh,
      motor: true,
      anchor: [0, 1.05],
      limit: [-150.deg, 0.deg],
      ctrllimit: [-200.deg, 200.deg]
    )
    joint(
      type: :revolute,
      name: :leg_joint,
      bodyA: :thigh,
      bodyB: :leg,
      motor: true,
      anchor: [0, 0.6],
      limit: [-150.deg, 0.deg],
      ctrllimit: [-200.deg, 200.deg]
    )
    joint(
      type: :revolute,
      name: :foot_joint,
      bodyA: :leg,
      bodyB: :foot,
      motor: true,
      anchor: [0, 0.1],
      limit: [-45.deg, 45.deg],
      ctrllimit: [-200.deg, 200.deg]
    )
  }
}
