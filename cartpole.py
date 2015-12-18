from box2d_mdp import Box2DMDP


def main():
    import time
    mdp = Box2DMDP("cartpole.xml")
    state, _ = mdp.reset()
    mdp.start_viewer()
    for _ in range(1000):
        state, _ = mdp.step(state, [10])
        mdp.plot()
        time.sleep(1.0/60)
    mdp.stop_viewer()

if __name__ == "__main__":
    main()
