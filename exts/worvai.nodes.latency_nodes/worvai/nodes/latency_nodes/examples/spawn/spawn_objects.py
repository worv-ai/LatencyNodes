import numpy as np
import omni
import carb
from pxr import Sdf, UsdLux, UsdGeom, Gf, UsdPhysics, PhysxSchema
from isaacsim.core.prims import SingleXFormPrim
from isaacsim.storage.native import get_assets_root_path
from isaacsim.core.utils.stage import add_reference_to_stage
from omni.physx.scripts import physicsUtils

ASSET_ROOT_PATH = get_assets_root_path()

if ASSET_ROOT_PATH is None:
    carb.log_error("Could not find Isaac Sim assets folder")


def spawn_ground_plane(world):
    material_blue_steel_cold = "/NVIDIA/Materials/vMaterials_2/Metal/Blued_Steel_Cold.mdl"

    ground_plane_path = "/World/defaultGroundPlane"
    material_prim_path = "/World/Looks/BluedSteelCold"

    world.scene.add_ground_plane(
        z_position=0,
        name="default_ground_plane",
        prim_path=ground_plane_path,
        static_friction=0.2,
        dynamic_friction=0.2,
        restitution=0.01,
    )

    success, log = omni.kit.commands.execute(
        "CreateMdlMaterialPrim",
        mtl_url=f"{ASSET_ROOT_PATH}{material_blue_steel_cold}",
        mtl_name="Blued_Steel_Cold",
        mtl_path=material_prim_path,
    )
    if not success:
        carb.log_error(f"Failed to create material: {log}")

    omni.kit.commands.execute(
        "BindMaterial",
        prim_path=ground_plane_path,
        material_path=material_prim_path,
    )


def spawn_light(world):
    stage = world.stage
    dome_path = Sdf.Path("/World/SkyDome")

    dome = UsdLux.DomeLight.Define(stage, dome_path)
    dome.CreateIntensityAttr(3500.0)
    dome.CreateTextureFileAttr("")
    dome.CreateSpecularAttr(True)
    dome.CreateColorAttr(Gf.Vec3f(0.3, 0.3, 0.3))


def spawn_background_objects(
    world, 
    num, 
    min_radius=2.0, 
    max_radius=50.0, 
    forward_angle_deg=150, 
    height_range=(0.1, 10.0)
):
    """
    Spawns random objects in a specified zone, avoiding the origin and focusing
    on a forward-facing direction (positive X-axis).

    Args:
        world: The Isaac Sim world object.
        num (int): The number of objects to spawn.
        min_radius (float): The radius of the exclusion zone around the origin.
        max_radius (float): The maximum radius for spawning objects.
        forward_angle_deg (float): The angular width (in degrees) of the forward-facing spawn cone.
        height_range (tuple): A tuple (min_z, max_z) for the spawn height.
    """
    forward_angle_rad = np.deg2rad(forward_angle_deg)
    max_angle = forward_angle_rad / 2
    min_angle = max_angle * 0.2

    xy_history = []
    prims = []

    for i in range(num):
        # == Using polar coordinates, choose random spawnpoint ==
        while True:
            radius = np.random.uniform(min_radius, max_radius)
            angle = np.random.uniform(min_angle, max_angle)

            if np.random.rand() > 0.5:
                angle = -angle

            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Check if the position is too close to previously spawned objects
            if not any(
                np.linalg.norm(np.array([x, y]) - np.array(pos[:2])) < 0.5
                for pos in xy_history
            ):
                xy_history.append((x, y))
                break
        
        # === Random height ===
        z = np.random.uniform(height_range[0], height_range[1])
        
        position = np.array([x, y, z])

        # === Random orientation ===
        orientation = np.random.uniform(-1, 1, size=4)
        orientation /= np.linalg.norm(orientation) # Normalize

        # === Random scale ===
        scale = np.random.lognormal(mean=-2.5, sigma=0.8)
        scale = np.clip(scale, 0.02, 0.5)
        scale_vec = np.array([scale] * 3)

        if np.random.rand() > 0.5:
            prim = spawn_mug_nvidia(world, position, orientation, scale_vec, i)
        else:
            # Note: The Rubik's cube asset is much smaller, so a larger scale factor is needed.
            prim = spawn_cube_rubiks(world, position, orientation, 100 * scale_vec, i)

        prims.append(prim)

    return prims

def spawn_mug_nvidia(world, position, orientation, scale, name):
    mug_nvidia = "/Isaac/Props/Mugs/SM_Mug_A2.usd"
    prim_path = f"/World/objects/mug_nvidia_{name}"
    add_reference_to_stage(
        usd_path=f"{ASSET_ROOT_PATH}{mug_nvidia}",
        prim_path=prim_path,
        prim_type="Xform"
    )

    SingleXFormPrim(
        prim_path=prim_path,
        position=position,
        orientation=orientation,
        scale=scale,
    )
    prim = world.stage.GetPrimAtPath(prim_path)

    rigid_api = UsdPhysics.RigidBodyAPI.Apply(prim)
    rigid_api.CreateRigidBodyEnabledAttr(True)
    UsdPhysics.CollisionAPI.Apply(prim)
    mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim)
    mesh_collision_api.CreateApproximationAttr().Set("convexHull")

    return prim

def spawn_cube_rubiks(world, position, orientation, scale, name):
    cube_rubiks = "/Isaac/Props/Rubiks_Cube/rubiks_cube.usd"
    prim_path = f"/World/objects/cube_rubiks_{name}"
    add_reference_to_stage(
        usd_path=f"{ASSET_ROOT_PATH}{cube_rubiks}",
        prim_path=prim_path,
        prim_type="Xform"
    )

    SingleXFormPrim(
        prim_path=prim_path,
        position=position,
        orientation=orientation,
        scale=scale,
    )
    prim = world.stage.GetPrimAtPath(prim_path)

    rigid_api = UsdPhysics.RigidBodyAPI.Apply(prim)

    rigid_api.CreateRigidBodyEnabledAttr(True)
    UsdPhysics.CollisionAPI.Apply(prim)
    mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim)
    mesh_collision_api.CreateApproximationAttr().Set("convexHull")

    return prim

def spawn_light_ball(world, position, orientation, scale, name):
    # TODO: add embodied one

    light_prim_path = f"{prim_path}/SphereLight"
    light_prim = UsdLux.SphereLight.Define(
        world.stage,
        Sdf.Path(light_prim_path)
    )
    light_prim.GetTreatAsPointAttr().Set(True)

    rigid_api = UsdPhysics.RigidBodyAPI.Apply(prim)
    rigid_api.CreateRigidBodyEnabledAttr(True)
    UsdPhysics.CollisionAPI.Apply(prim)
    mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prim)

    return light_prim