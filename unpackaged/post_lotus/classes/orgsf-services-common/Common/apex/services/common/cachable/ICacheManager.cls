public interface ICacheManager {
    String getPartitionName();
    Set<String> getKeys();
    Object getValueForKey(String key);
    Boolean deleteFromCache(String key);
}