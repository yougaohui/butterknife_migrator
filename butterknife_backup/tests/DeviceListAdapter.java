package com.onmicro.omtoolbox.scanner;
import android.bluetooth.BluetoothDevice;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.onmicro.omtoolbox.R;
import com.onmicro.omtoolbox.R2;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
public class DeviceListAdapter extends RecyclerView.Adapter<DeviceListAdapter.MyViewHolder> {
    private List<ExtendedBluetoothDevice> devices = new ArrayList<>();
    private boolean isClick;
    private View.OnClickListener onClickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (onItemClickListener != null) {
                onItemClickListener.onItemClick((int) v.getTag());
            }
        }
    };
    private View.OnTouchListener onTouchListener = new View.OnTouchListener() {
        @Override
        public boolean onTouch(View v, MotionEvent event) {
            switch (event.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    isClick = true;
                    break;
                case MotionEvent.ACTION_MOVE:
                    break;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    isClick= false;
                    break;
            }
            return false;
        }
    };
    public void addDevice(BluetoothDevice bluetoothDevice, int rssi) {
        ExtendedBluetoothDevice device = findDevice(bluetoothDevice);
        if (device == null) {
            devices.add(new ExtendedBluetoothDevice(bluetoothDevice, rssi));
        } else {
            device.rssi = rssi;
        }
        if (!isClick) {
            notifyDataSetChanged();
        }
    }
    private ExtendedBluetoothDevice findDevice(@NonNull final BluetoothDevice bluetoothDevice) {
        if (devices != null && !devices.isEmpty()) {
            for (final ExtendedBluetoothDevice device : devices) {
                if (device.matches(bluetoothDevice)) {
                    return device;
                }
            }
        }
        return null;
    }
    public void clear() {
        devices.clear();
        notifyDataSetChanged();
    }
    public void sort() {
        Collections.sort(devices, (o1, o2) -> o2.rssi - o1.rssi);
        notifyDataSetChanged();
    }
    public ExtendedBluetoothDevice getItemAtPosition(int position) {
        return devices.get(position);
    }
    public List<ExtendedBluetoothDevice> getDevices() {
        return devices;
    }
    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.recy_item_device_list, parent, false);
        return new MyViewHolder(itemView);
    }
    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        holder.itemView.setTag(position);
        ExtendedBluetoothDevice extendedBluetoothDevice = devices.get(position);
        BluetoothDevice bluetoothDevice = extendedBluetoothDevice.device;
        String name = bluetoothDevice.getName();
        String address = bluetoothDevice.getAddress();
        holder.tv_name.setText(TextUtils.isEmpty(name) ? "N/Y" : name);
        holder.tv_address.setText(address);
        holder.tv_rssi.setText(String.format(Locale.ROOT, "%ddBm", extendedBluetoothDevice.rssi));
        holder.itemView.setOnClickListener(onClickListener);
        holder.itemView.setOnTouchListener(onTouchListener);
    }
    @Override
    public int getItemCount() {
        return devices == null ? 0 : devices.size();
    }
    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tv_name;
        TextView tv_address;
        TextView tv_rssi;
        public MyViewHolder(View itemView) {
            super(itemView);
        // 初始化View绑定 - 替换@BindView注解
        tv_name = itemView.findViewById(R.id.tv_name);
        tv_address = itemView.findViewById(R.id.tv_address);
        tv_rssi = itemView.findViewById(R.id.tv_rssi);

        }
    }
    public interface OnItemClickListener {
        void onItemClick(int position);
    }
    private OnItemClickListener onItemClickListener;
    public void setOnItemClickListener(OnItemClickListener onItemClickListener) {
        this.onItemClickListener = onItemClickListener;
    }
}