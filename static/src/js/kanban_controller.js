/** @odoo-module */

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

const KanbanControllerPatch = {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.effectService = useService("effect");
        this.orm = useService("orm");
    },

    async syncProducts() {
        console.log(this.props);
        try {
            const response = await this.orm.call(
                'product.template',
                'action_sync_products',
            );
        } catch (error) {
            console.error("Error calling  method:", error);
        }

        this.effectService.add({
            type: "rainbow_man",
            message: "Data Synced successfully",
            fadeout: "slow"
        });

         setTimeout(() => {
            this.actionService.doAction({
                type: 'ir.actions.client',
                tag: 'reload',
            });
        }, 3000);
    }
}

patch(KanbanController.prototype, KanbanControllerPatch);