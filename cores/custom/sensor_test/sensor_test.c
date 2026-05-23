/* sensor_test — exercises RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE. */

#include "sample_common.h"

static struct retro_sensor_interface sensor;

static bool sensor_load_game(const struct retro_game_info *info)
{
    (void)info;
    if (!sample_environ_cb(RETRO_ENVIRONMENT_GET_SENSOR_INTERFACE, &sensor))
    {
        sensor.set_sensor_state = NULL;
        sensor.get_sensor_input = NULL;
    }
    if (sensor.set_sensor_state)
        sensor.set_sensor_state(0, RETRO_SENSOR_ACCELEROMETER_ENABLE, 60);
    return true;
}

static void sensor_run_frame(void)
{
    if (!sensor.get_sensor_input)
        return;

    (void)sensor.get_sensor_input(0, RETRO_SENSOR_ACCELEROMETER_X);
    (void)sensor.get_sensor_input(0, RETRO_SENSOR_ACCELEROMETER_Y);
    (void)sensor.get_sensor_input(0, RETRO_SENSOR_ACCELEROMETER_Z);
}

static void sensor_unload_game(void)
{
    if (sensor.set_sensor_state)
        sensor.set_sensor_state(0, RETRO_SENSOR_ACCELEROMETER_DISABLE, 0);
}

const struct sample_core_def sample_core = {
    .load_game   = sensor_load_game,
    .unload_game = sensor_unload_game,
    .run_frame   = sensor_run_frame,
};
